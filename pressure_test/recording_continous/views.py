from django.shortcuts import render
import os, re, datetime, time, json
from django.shortcuts import render
from collections import Counter
from rest_framework.response import Response
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import permissions

from config.models import ProjectSetting
from libs.nas_storage import NasStorage

from recording_continous.models import RecordingContinuty
from recording_continous.models import RecordingFile
from recording_continous.models import Config

from recording_continous.video_continous import VideoContinous
from rest_framework.decorators import api_view, permission_classes
from recording_continous.tasks import arrange_periodic_task
from recording_continous.monitor import Monitor
from recording_continous import monitor
from django.utils.timezone import localtime
import pexpect
from datetime import timezone
import pytz


from libs.vast_storage import VastStorage

def order_vast_file(clips):
    clips_timelist = []
    sorted_filelist = []
    for file_path in clips:
        local_path = os.path.join("/mnt/", os.path.dirname(file_path).replace('//', '').replace('/', '_'))
        clippath = os.path.join(local_path, os.path.basename(file_path))

        clip_modify_time = os.stat(clippath).st_mtime

        clips_timelist.append([clip_modify_time, file_path])
    for i in sorted(clips_timelist):
        sorted_filelist.append(i[1])
    return sorted_filelist

@api_view(['GET'])
@permission_classes((permissions.AllowAny,))
def ana_videos(request, project_id):
    # print ("init")
    # query = ProjectSetting.objects.get(id=project_id)
    # start_time = localtime(query.start_time)
    # end_time = localtime(query.end_time)
    # path = query.path
    #
    # # vs=VastStorage()
    # # clips = vs.get_video_vast('ptest', 'ptest', '', '//172.19.11.189/Ptest/2017-06-23/37-FD816B-HT', start_time, end_time)
    # print ("++++++++++++++++")
    # print ("go")
    # ns =NasStorage()
    # print ("++++++++++++++++")
    # print ("mount")
    # print ("++++++++++++++++")
    # clips = ns.get_video_nas('autotest', 'autotest', '', "//172.19.11.189/Public/autotest/press_test", "medium_stress", start_time, end_time)
    #
    #
    # # clips = order_vast_file(clips)
    # print ("++++++++++++++++")
    # print (clips)
    # print (end_time)
    # print ("++++++++++++++++")
    #
    # return Response(' : '.join(clips))

    response = analyze_videos(project_id)
    return Response(response)


def analyze_videos(project_id):
    query = ProjectSetting.objects.get(id=project_id)
    if not query.continued:
        return Response({'message': "Not project setting for continuous_test"})
    start_time = localtime(query.start_time)
    end_time = localtime(query.end_time)
    print ('********video_continuous**********')
    print (start_time)
    print (end_time)
    print ('********video_continuous**********')

    interval_time = datetime.timedelta(hours=1)
    from recording_continous.tasks import arrange_periodic_task
    from recording_continous.monitor import Monitor
    from recording_continous import monitor
    import pexpect
    # add consumer for celery
    cmd = "/home/dqa/code/env/bin/celery -A pressure_test control add_consumer continous_test_camera{}".format(
        project_id)
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
            (project_id, start_time, end_time)
        )
    m.start()
    monitor.camera_id_2_monitor[str(project_id)] = m
    # print("monitor: ", monitor.camera_id_2_monitor)
    return {'message': "Insert camera into schedule successfully", 'project_id': project_id}


@api_view(['GET'])
@permission_classes((permissions.AllowAny,))
def running_status(request, project_id):
    response = continuous_running_status(project_id)
    return Response(response)


def continuous_running_status(project_pk):
    INVALID_PROJ_ID = 'invalid project id'
    INVALID_MONITOR_ID = 'invalid monitor id'
    FINISHED = 'finished'
    # get project object
    project = ProjectSetting.objects.filter(id=project_pk).first()
    status = INVALID_PROJ_ID
    queue_size = 0
    next_schedule = []
    if str(project_pk) in monitor.camera_id_2_monitor.keys():
        m = monitor.camera_id_2_monitor[str(project_pk)]
        if m:
            status, queue_size, next_schedule = m.get_schedule_status()
        else:
            status = FINISHED
    else:
        status = INVALID_MONITOR_ID

    return {'status': status, 'size': queue_size, 'next schedule': next_schedule}


@api_view(['GET'])
@permission_classes((permissions.AllowAny, ))
def stop_continuous_test_process(request, project_id):
    response = stop_continuous_test(project_id)
    return Response(response)


def stop_continuous_test(project_pk):
    # get project object
    project = ProjectSetting.objects.get(id=project_pk)
    # search camera with project
    # index 0 is because project vs camera is 1:1 now
    if str(project_pk) in monitor.camera_id_2_monitor.keys():
        m = monitor.camera_id_2_monitor[str(project_pk)]
        m.stop()
    else:
        return {'message': "No Secdule", 'id': project_pk}
    return {'message': "Cancel camera from schedule successfully", 'project_name': project_pk}


#*********************************
#*****Create your views here.*****
#*********************************
@api_view(['GET'])
@permission_classes((AllowAny,))
def implement_in(requests):
    vc = VideoContinous("/home/carlos/pressure_final/pressure_test_backend/pressure_test/recording_continous/125.3gp","/home/carlos/pressure_final/pressure_test_backend/pressure_test/recording_continous/126.3gp")
    in_result=vc.continuity_in_recording_files()
    between_result=vc.continuity_bwtween_recording_files()

    RecordingContinuty.objects.create(
        project_id='124_125',
        creat_at=in_result["creat_at"],
        video_path=in_result["video_path"],
        size=in_result["size"],
        in_result=in_result["in_result"],
        error_code=in_result["error_code"],
        start_time=in_result["start_time"],
        end_time=in_result["start_time"],
        link=in_result["link"],
        count=in_result["count"],
        between_result=between_result["between_result"],
        seconds=between_result["seconds"],

    )
    return Response('Done')


@api_view(['GET'])
@permission_classes((AllowAny,))
def continuous_report(requests, project_id):
    query = RecordingContinuty.objects.filter(project_id=project_id)
    # query = RecordingContinuity.objects.filter(project_id=project_id).order_by("video_path")
    result = {}
    result["id"] = project_id
    result["data"] = []

    for i in query:
        result_detail ={}
        result_detail["createAt"] = i.creat_at
        result_detail["path"] = i.video_path
        result_detail["videoPathBefore"] = i.video_path_before
        result_detail["size"] = i.size
        result_detail["in"] = i.in_result
        result_detail["errorCode"] = i.error_code
        result_detail["startTime"] = i.start_time
        result_detail["endTime"] = i.end_time
        result_detail["link"] = i.link
        result_detail["count"] = i.count
        result_detail["between"] = i.between_result
        result_detail["second"] = i.seconds

        result["data"].append(result_detail)

    return HttpResponse(json.dumps(result))
