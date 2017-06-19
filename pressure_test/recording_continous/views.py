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

import pexpect

# Create your views here.

@api_view(['GET'])
@permission_classes((AllowAny,))
def implement_in(requests):
    vc = VideoContinous("18.mp4","19.mp4")
    in_result=vc.continuity_in_recording_files()
    between_result=vc.continuity_bwtween_recording_files()

    RecordingContinuty.objects.create(
        project_id='1',
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
    return Response('done')


@api_view(['GET'])
@permission_classes((permissions.AllowAny,))
def ana_videos(request, project_id):
    # ns = NasStorage()
    # obj = ProjectSetting.objects.get(project_name=project_id)
    # remote_path = obj.path
    # remote_username = obj.path_username
    # remote_password = obj.path_password
    # sudo_password = ""
    # prefix = obj.prefix_name
    # time_start = obj.start_time
    # time_end = obj.end_time
    # a = []
    # a = ns.get_video_nas(remote_username, remote_password, sudo_password, remote_path, prefix, time_start, time_end)
    #
    # return Response({"result": len(a), "data": '\r\n'.join(a)})


    query = Config.objects.get(pk=2)
    start_time = datetime.datetime.strptime(query.start_time, "%Y-%m-%d %H:%M:%S")
    end_time = datetime.datetime.strptime(query.end_time, "%Y-%m-%d %H:%M:%S")
    print ('******************')
    print (start_time)
    print (end_time)
    print ('******************')
    # query = ProjectSetting.objects.get(id=int(project_id))
    # start_time = query.start_time
    # end_time = query.end_time

    interval_time = datetime.timedelta(hours=1)

    from recording_continous.tasks import arrange_periodic_task
    from recording_continous.monitor import Monitor
    from recording_continous import monitor
    import pexpect
    # add consumer for celery
    cmd = "/home/dqa/code/env/bin/celery -A pressure_test control add_consumer continous_test_camera{}".format(project_id)
    p = pexpect.spawn(cmd)
    # print(cmd)
    time.sleep(3)
    # add scheduler every hour
    periodic_check_points = []
    while start_time < end_time:
        periodic_check_points.append(start_time)
        start_time += interval_time
    periodic_check_points.append(end_time)

    m = Monitor()
    start_time_periodic_check_points = periodic_check_points[:-1]
    end_time_periodic_check_points = periodic_check_points[1:]

    for start_time, end_time in zip(start_time_periodic_check_points, end_time_periodic_check_points):
        m.add_periodic_jobs(
            time.mktime(end_time.timetuple()),
            arrange_periodic_task,
            (project_id, start_time, end_time)
        )
    # for period_time in periodic_check_points:
    #     m.add_periodic_jobs(
    #         time.mktime(period_time.timetuple()),
    #         #todo
    #         arrange_periodic_task,
    #         (project_id,)
    #         # todo
    #     )
    m.start()
    monitor.camera_id_2_monitor[str(project_id)] = m
    print("monitor: ", monitor.camera_id_2_monitor)
    return Response({'message': "Insert camera into schedule successfully", 'project_id': project_id })


@api_view(['GET'])
@permission_classes((AllowAny,))
def continous_report(requests, project_id):
    query = RecordingContinuty.objects.filter(project_id=project_id)
    # query = RecordingContinuty.objects.filter(project_id=project_id).order_by("video_path")
    result = {}
    result["id"] = project_id
    result["data"] = []

    for i in query:
        result_detail ={}
        result_detail["creatAt"] = i.creat_at
        result_detail["path"] = i.video_path
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