from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions
from rest_framework.response import Response
from collections import defaultdict
from functools import partial
from django.http import HttpResponse
from broken_tests.models import ClipInfo, CameraProfile, NasProfile, BrokenFrame
from broken_tests.serializers import ClipInfoSerializer, CameraProfileSerializer, NasProfileSerializer, BrokenFrameSerializer 
from rest_framework import generics
from broken_tests.helpers.content_analysis import ContentAnalysis
from broken_tests.helpers.roi_module import RoiModule
import time
import os
import datetime
from broken_tests.tasks import arrange_periodic_task
from broken_tests.helpers.monitor import Monitor
from broken_tests.helpers import monitor
from config.models import ProjectSetting
import pexpect
import glob
import json
import shutil
import re
from django.core.cache import cache
from django.conf import settings 


# Create your views here.
def module_pretest_broken_image(camera_host, camera_user, camera_password):
    # detect broken
    try:
        anly = ContentAnalysis()
        #   1. get snapshot to local folder
        roi = RoiModule(camera_host, camera_user, camera_password, 'NAS')
        stream_id = roi.get_recording_source()
        pretest_dir = time.time()
        anly(camera_host, camera_user, camera_password).save_snapshot_to_dir(
            '/home/dqa/data/pretests/{}'.format(pretest_dir),
            stream_id
        )
        #   2. get privacy mask
        roi = RoiModule(camera_host, camera_user, camera_password, 'NAS')
        names_to_corners = roi.return_mask()
        #   3. check broken
        privacy_mask_list = list(map(anly.trans_from_points_to_box, names_to_corners.values()))
        # privacy_mask_list = [
        #     anly.trans_from_points_to_box(names_to_corners['mask_up']),
        #     anly.trans_from_points_to_box(names_to_corners['mask_down']),
        #     anly.trans_from_points_to_box(names_to_corners['mask_left']),
        #     anly.trans_from_points_to_box(names_to_corners['mask_right']) ]

        frames = glob.glob(os.path.join('/home/dqa/data/pretests/{}'.format(pretest_dir), '*.jpg'))
        params = (privacy_mask_list, frames[0])
        results = anly.check_single_image_as_usual(params)
    except Exception as e:
        results = e

    return results


@api_view(['GET'])
@permission_classes((permissions.AllowAny, ))
def pretest_broken_image(request):
    # get query params
    camera_host = request.query_params.get('host', None)
    camera_user = request.query_params.get('user', None)
    camera_password = request.query_params.get('password', None)
    print("host: ", camera_host)
    print("user: ", camera_user)
    print("password: ", camera_password)
    # call core module
    results = module_pretest_broken_image(camera_host, camera_user, camera_password)
    print( results )
    return Response({'results': results['result'], 'error_boxes': results['error_boxes']})
    

@api_view(['GET'])
@permission_classes((permissions.AllowAny, ))
def running_status(request, project_pk):
    INVALID_PROJ_ID = 'invalid project id'
    INVALID_MONITOR_ID = 'invalid monitor id'
    FINISHED = 'finished'
    # get project object
    project = ProjectSetting.objects.filter(id=project_pk).first()
    status = INVALID_PROJ_ID
    queue_size = 0
    next_schedule = []
    if project:
        camera = project.cameraprofile_set.values()[0]
        if str(camera['id']) in monitor.camera_id_2_monitor.keys():
            m = monitor.camera_id_2_monitor[str(camera['id'])]
            if m:
                status, queue_size, next_schedule = m.get_schedule_status()
                # print('scheduleObj: ', schedule_obj)
            else:
                status = FINISHED
        else:
            status = INVALID_MONITOR_ID
        
        
    return Response({'status': status, 'size': queue_size, 'next schedule': next_schedule})


@api_view(['GET'])
@permission_classes((permissions.AllowAny, ))
def detect_periodic_videos(request, project_pk):
    # get project object
    project = ProjectSetting.objects.get(id=project_pk)
    if not project.broken:
        return Response({'message': "Not project setting for broken"})

    # start_time = project.start_time
    # end_time = project.end_time
    start_time = datetime.datetime.strptime("2017-06-20 19:00:00", "%Y-%m-%d %H:%M:%S")
    end_time = datetime.datetime.strptime("2017-06-21 09:30:00", "%Y-%m-%d %H:%M:%S")
    interval_time = datetime.timedelta(hours=1)
    # search camera with project
    # index 0 is because project vs camera is 1:1 now
    camera = project.cameraprofile_set.values()[0]
    # index 0 is because project vs nas is 1:1 now
    nas = project.nasprofile_set.values()[0]
    
    # add consumer for celery
    cmd = "/home/dqa/code/env/bin/celery -A pressure_test control add_consumer broken_test_camera{}".format(camera['id'])
    p = pexpect.spawn(cmd)
    print(cmd)
    time.sleep(3)
    # add scheduler every hour
    periodic_check_points = []
    periodic_time = start_time
    while periodic_time < end_time:
        periodic_check_points.append(periodic_time)
        periodic_time += interval_time
    periodic_check_points.append(end_time)

    print("periodic points: ", periodic_check_points)
    m = Monitor()
    for periodic_time in periodic_check_points:
        m.add_periodic_jobs(
            time.mktime(periodic_time.timetuple()),
            arrange_periodic_task,
            (camera['id'], nas['id'], start_time, end_time) 
         )
    m.start()
    monitor.camera_id_2_monitor[str(camera['id'])] = m
    print("monitor: ", monitor.camera_id_2_monitor)
    return Response({'message': "Insert camera into schedule successfully", 'camera_id': camera['id']})

    
@api_view(['GET'])
@permission_classes((permissions.AllowAny, ))
def stop_detect_periodic_videos(request, project_pk):
    # get project object
    project = ProjectSetting.objects.get(id=project_pk)

    # search camera with project
    # index 0 is because project vs camera is 1:1 now
    camera = project.cameraprofile_set.values()[0]
    if str(camera['id']) in monitor.camera_id_2_monitor.keys():
        m = monitor.camera_id_2_monitor[str(camera['id'])]
        m.stop()

    # cancel consumer of celery
    cmd = "/home/dqa/code/env/bin/celery -A pressure_test control cancel_consumer broken_test_camera{}".format(camera['id'])
    p = pexpect.spawn(cmd)
    print( cmd )
    time.sleep(3)

    # clear tasks from a specific queue by id
    cmd = "/home/dqa/code/env/bin/celery -A pressure_test purge -Q broken_test_camera{} -f".format(camera['id'])
    p = pexpect.spawn(cmd)
    print( cmd )
    time.sleep(3)

    return Response({'message': "Cancel camera from schedule successfully", 'camera_id': camera['id']})


def detect_broken_image(pk):

    print("pk= ", pk)
    # filter clip object by id
    clip = ClipInfo.objects.get(id=pk)
    camera = clip.camera_profile
    nas = clip.nas_profile
    
    # detect broken
    anly = ContentAnalysis()
    #   1. mount folder
    local_path = os.path.join("/mnt/", nas.location.replace('//', '').replace('/', '_'))
    is_mounted = anly.mount_folder(
        nas.user,
        nas.password,
        nas.location,
        '',
        local_path)
    print("local path= ", local_path)
    print("is_mounted= ", is_mounted)
    clippath = os.path.join(local_path, clip.full_path.lower()[len(nas.location)+1:])
    # framefolder = os.path.join(os.path.dirname(clippath), 'broken', os.path.splitext(os.path.basename(clippath))[0])
    framefolder = os.path.join(os.path.dirname(clippath), 'broken', '_'.join([os.path.splitext(os.path.basename(clippath))[0], str(time.time())]))
    print("clippath= ", clippath)
    print("framefolder= ", framefolder)
    # #   1-1. remove framefolder if exists
    # if os.path.exists(framefolder):
    #     shutil.rmtree(framefolder)
    #   2. cut to frames
    anly.cut_to_frames(
        clippath,
        framefolder
    )
    #   3. check broken
    print("clipprivacy= ", clip.privacy_masks)
    privacy_mask_list = list(map(anly.trans_from_points_to_box, eval(clip.privacy_masks).values()))
    # names_to_corners = eval(clip.privacy_masks)
    # privacy_mask_list = [ 
    #     anly.trans_from_points_to_box(names_to_corners['mask_up']),
    #     anly.trans_from_points_to_box(names_to_corners['mask_down']),
    #     anly.trans_from_points_to_box(names_to_corners['mask_left']),
    #     anly.trans_from_points_to_box(names_to_corners['mask_right']) ]

    video_status = anly.check_video_frames_as_usual_v3(
        framefolder,
        privacy_mask_list
    )

    # # create brokenInfo
    # video_status = {
    #     'result': 'failed',
    #     'failed_frames': [
    #         {
    #             'error_message': "decoede error",
    #             'path': "a/b/c.mp4"
    #         },
    #         {
    #             'error_message': "decoede error",
    #             'path': "a/b/c.mp4"
    #         },
    #     ] }
    for failed_frame in video_status['failed_frames']:
        print("each failed frame: ", failed_frame)
        m = re.search(r"mul(?P<timestamp>[0-9]+).jpg", failed_frame['path'])
        BrokenFrame.objects.create(
            error_message=failed_frame['error_message'],
            frame_path=failed_frame['path'],
            clip=clip,
            timestamp=datetime.timedelta(seconds=round(int(m.group('timestamp'))/2, 1)) if m else None # FPS=2
        )

    print( "video_status: ", video_status )

    # update analysis info
    clip.size = os.path.getsize(clippath)
    clip.is_broken = False if video_status['result'] == 'passed' else True
    clip.save()

    # return clip


# def no_such_action_to_analysis(pk, action):
#     return 'Sorry, no such action ({}) to analysis'.format(action)


# @api_view(['GET'])
# @permission_classes((permissions.AllowAny, ))
# def detect_video(request, pk, action):
#     print("action-----------------------")
#     print("act={}".format(action))
#     print("pk={}".format(pk))
#     support_actions = { 'detectbroken': detect_broken_image, }
#     action_options = defaultdict(lambda: partial(no_such_action_to_analysis, action), support_actions)
#     msg = action_options[action]
    
#     return HttpResponse(msg(pk))


@api_view(['GET'])
@permission_classes((permissions.AllowAny, ))
def broken_report(requests, project_pk):
   clips = ClipInfo.objects.filter(camera_profile__project_profile__id=project_pk)

   result = {}
   result["id"] = project_pk
   result["data"] = []    
   for i in clips:
       result_detail ={}
       result_detail["path"] = i.path
       result_detail["size"] = i.size
       result_detail["result"] = i.result
       result_detail["errorCode"] = i.errorCode
       result_detail["link"] = i.link
       result_detail["count"] = i.count
       
       result["data"].append(result_detail)    
    
   return Response(result)


class ClipInfoDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ClipInfo.objects.all()
    serializer_class = ClipInfoSerializer


class ClipInfoList(generics.ListCreateAPIView):
    queryset = ClipInfo.objects.all()
    serializer_class = ClipInfoSerializer

    def get_queryset(self):
        """
        This view should return a list of all the purchases for
        the user as determined by the username portion of the URL.
        """
        project_id = self.kwargs['project_pk']
        return ClipInfo.objects.filter(camera_profile__project_profile__id=project_id)


class CameraProfileDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = CameraProfile.objects.all()
    serializer_class = CameraProfileSerializer


class CameraProfileList(generics.ListCreateAPIView):
    queryset = CameraProfile.objects.all()
    serializer_class = CameraProfileSerializer


class NasProfileDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = NasProfile.objects.all()
    serializer_class = NasProfileSerializer


class NasProfileList(generics.ListCreateAPIView):
    queryset = NasProfile.objects.all()
    serializer_class = NasProfileSerializer


class BrokenFrameDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = BrokenFrame.objects.all()
    serializer_class = BrokenFrameSerializer


class BrokenFrameList(generics.ListCreateAPIView):
    queryset = BrokenFrame.objects.all()
    serializer_class = BrokenFrameSerializer