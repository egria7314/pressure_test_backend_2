# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from config.serializers import ProjectSettingSerializer
from rest_framework import generics
from config.models import ProjectSetting
from recording_continous.models import RecordingFile
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from config.models import DefaultSetting
from libs.nas_storage import NasStorage
from rest_framework import status
from rest_framework.decorators import api_view
from django.utils.timezone import localtime
from libs.telnet_module import URI
from recording_continous.views import analyze_videos
from camera_log.views import run_cameralog_schedule_by_id
from broken_tests.views import module_detect_periodic_videos
import re, collections
from threading import Thread
import time


class ProjectSettingDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProjectSetting.objects.all()
    serializer_class = ProjectSettingSerializer


class ProjectSettingList(generics.ListCreateAPIView):
    queryset = ProjectSetting.objects.all()
    serializer_class = ProjectSettingSerializer


@api_view(['POST'])
@permission_classes((AllowAny,))
def post(request):
    serializer = ProjectSettingSerializer(data=request.data)
    camera_ip = request.data['ip']
    camera_user = request.data['username']
    camera_password = request.data['password']
    prefix_name = get_recording_prefix(camera_ip, camera_user, camera_password)
    request.data['prefix_name'] = prefix_name
    if serializer.is_valid():
        a = serializer.save()
        project_id = a.id
        analyze_videos(project_id=project_id)
        run_cameralog_schedule_by_id(project_id=project_id)
        module_detect_periodic_videos(project_pk=project_id)
        result = {'createCheck':True, "status":status.HTTP_201_CREATED, "action":"create data", "data":serializer.data, "comment":"create success"}
        return Response(result, status=status.HTTP_201_CREATED)

    result = {'createCheck':False, "status":status.HTTP_400_BAD_REQUEST, "action":"create data", "data":serializer.data, "comment":str(serializer.errors)}
    return Response(result)

def get_recording_type(camera_ip, camera_name, camera_password):
    """Get nas location from camera by cgi"""
    type_code = None
    for index in range(2):
        command = 'http://'+camera_ip+'/cgi-bin/admin/getparam.cgi?recording_i{0}_dest'.format(index)
        try:
            url = URI.set(command, camera_name, camera_password)
            url = url.read().decode('utf-8').split("\r\n")
            result = url[0].replace('recording_i{0}_dest'.format(index), '').replace("'", "").replace("=", "")
            if result != 'cf':
                type_code = index
                break
            else:
                continue
        except:
            type_code = 'get recording type error'

    return type_code

def get_recording_prefix(camera_ip, camera_name, camera_password):
    """Get nas location from camera by cgi"""
    index = get_recording_type(camera_ip, camera_name, camera_password)
    command = 'http://'+camera_ip+'/cgi-bin/admin/getparam.cgi?recording_i{0}_prefix'.format(index)

    prefix = None
    try:
        url = URI.set(command, camera_name, camera_password)
        url = url.read().decode('utf-8').split("\r\n")
        result = url[0].replace('recording_i{0}_prefix'.format(index), '').replace("'", "").replace("=", "")
        prefix = result
    except:
        prefix = 'get recording prefix error'
    finally:
        return prefix

@api_view(['GET'])
@permission_classes((AllowAny,))
def init_default_setting(requests):
    default_json = [
        {
            'default_type': 'medium',
            'log_sd_card_status': True,
            'log_cyclic_recording': True,
            'log_nas_recording': True,
            'broken_image': True,
            'cont_inner_serial_timstamp': True,
            'cont_outer_serial_timstamp': True,
            'delay': 2,
            'cgi': 180
        },
        {
            'default_type': 'high',
            'log_sd_card_status': True,
            'log_cyclic_recording': True,
            'log_nas_recording': True,
            'broken_image': True,
            'cont_inner_serial_timstamp': False,
            'cont_outer_serial_timstamp': False,
            'delay': 5,
            'cgi': 300
        }
    ]
    for default in default_json:
        DefaultSetting.objects.create(
                default_type = default['default_type'],
                log_sd_card_status = default['log_sd_card_status'],
                log_cyclic_recording = default['log_cyclic_recording'],
                log_nas_recording = default['log_nas_recording'],
                broken_image = default['broken_image'],
                cont_inner_serial_timstamp = default['cont_inner_serial_timstamp'],
                cont_outer_serial_timstamp = default['cont_outer_serial_timstamp'],
                delay = default['delay'],
                cgi = default['cgi']
            )
    A = {'result': 'pass'}
    return Response(A)

@api_view(['GET'])
@permission_classes((AllowAny,))
def return_default_setting(requests):
    return_json = {}
    mode = requests.GET['mode']
    querryset = DefaultSetting.objects.filter(default_type=mode)[0]
    if querryset.log_sd_card_status and querryset.log_cyclic_recording and querryset.log_nas_recording:
        return_json['log'] = True
    else:
        return_json['log'] = False
    if querryset.cont_inner_serial_timstamp and querryset.cont_outer_serial_timstamp:
        return_json['continuity'] = True
    else:
        return_json['continuity'] = False
    return_json['broken'] = querryset.broken_image
    return_json['cgi'] = querryset.cgi
    return_json['delay'] = querryset.delay
    return Response(return_json)

@api_view(['GET'])
@permission_classes((AllowAny,))
def return_nas_location(requests):
    ip = requests.GET['cameraip']
    name = requests.GET['username']
    pw = requests.GET['password']
    return_json = NasStorage().get_nas_location(ip, name, pw)
    return Response(return_json)

@api_view(['GET'])
@permission_classes((AllowAny,))
def return_project_setting(requests, pk=None):
    if pk:
        querry_set = ProjectSetting.objects.filter(id = pk).values("id", "path", "project_name", "start_time", "log", "delay", "end_time",
                                                     "path_username", "continued", "username", "type", "broken", "owner",
                                                     "prefix_name", "cgi", "password", "path_password", "ip")
        return_json = list(querry_set)[0]
        return_json['projectName'] = return_json.pop('project_name')
        return_json['cameraIp'] = return_json.pop('ip')
        return_json['startTime'] = return_json.pop('start_time')
        return_json['startTime'] = localtime(return_json['startTime'])
        return_json['endTime'] = return_json.pop('end_time')
        return_json['endTime'] = localtime(return_json['end_time'])

    else:
        querry_set = ProjectSetting.objects.all().values("id", "path", "project_name", "start_time", "log", "delay", "end_time",
                                                     "path_username", "continued", "username", "type", "broken", "owner",
                                                     "prefix_name", "cgi", "password", "path_password", "ip")
        return_json = list(querry_set)
        for item_json in return_json:
            item_json['projectName'] = item_json.pop('project_name')
            item_json['cameraIp'] = item_json.pop('ip')
            item_json['startTime'] = item_json.pop('start_time')
            item_json['startTime'] = localtime(item_json['startTime'])
            item_json['endTime'] = item_json.pop('end_time')
            item_json['endTime'] = localtime(item_json['endTime'])
    return Response(return_json)

@api_view(['GET'])
@permission_classes((AllowAny,))
def return_daily_summary(requests, pk):
    querry_set = RecordingFile.objects.filter(project_id = pk).values("project_id", "path")
    file_list = list(querry_set)
    transform_list =  transform_dict(file_list, pk)
    return_dict = {"id": str(pk), "data": transform_list}
    return Response(return_dict)

def transform_dict(file_list, p_id):
    querry_set = ProjectSetting.objects.filter(id = p_id).values("type")
    test_type = list(querry_set)[0]["type"]
    date_list = []
    transform_list = []
    for dict_item in file_list:
        if test_type != "medium":
            create_at = re.search('\d{8}', dict_item['path']).group(0)
        else:
            create_at = re.search('\d{4}\-\d{2}\-\d{2}', dict_item['path']).group(0)
        date_list.append(create_at)
    cnt = collections.Counter()
    for date in date_list:
        cnt[date] += 1
    date_count_dict = dict(cnt)
    for date, count in date_count_dict.items():
        transform_list.append({'createAt': date.replace('-', ''), 'count': count})
    return transform_list

