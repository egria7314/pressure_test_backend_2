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
from django.db.models import Q
from broken_tests import views as broken_views
from recording_continous import views as continue_views
from camera_log import views as log_views

from recording_continous.views import continuous_running_status
from broken_tests.views import module_running_status
from camera_log.views import running_status
import re, collections
from threading import Thread
import time,datetime, json
from django.db import connection


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
    request.data['path'] = request.data['path'].replace('\\', '/')
    if serializer.is_valid():
        a = serializer.save()
        project_id = a.id
        analyze_videos(project_id=project_id)
        run_cameralog_schedule_by_id(project_id=project_id)
        module_detect_periodic_videos(project_pk=project_id)
        ProjectSetting.objects.filter(id=project_id).update(continuity_status=continuous_running_status(project_pk=project_id)['status'],
                                                    log_status=running_status(project_pk=project_id)['status'],
                                                    broken_status=module_running_status(project_pk=project_id)[0])
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
    # for init default setting
    DefaultSetting.objects.all().delete()
    connection.cursor().execute('''SELECT setval('{0}', 1, false)'''.format('config_defaultsetting_id_seq'))

    with open('config/init_setting.json') as data_file:
        default_json = json.load(data_file)

    for default in default_json:
        DefaultSetting.objects.create(
                default_type = default["fields"]['default_type'],
                log_sd_card_status = default["fields"]['log_sd_card_status'],
                log_cyclic_recording = default["fields"]['log_cyclic_recording'],
                log_nas_recording = default["fields"]['log_nas_recording'],
                broken_image = default["fields"]['broken_image'],
                cont_inner_serial_timstamp = default["fields"]['cont_inner_serial_timstamp'],
                cont_outer_serial_timstamp = default["fields"]['cont_outer_serial_timstamp'],
                delay = default["fields"]['delay'],
                cgi = default["fields"]['cgi']
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
        query_set = ProjectSetting.objects.filter(id = pk).values("id", "path", "project_name", "start_time", "log", "delay", "end_time",
                                                     "path_username", "continued", "username", "type", "broken", "owner",
                                                     "prefix_name", "cgi", "password", "path_password", "ip", "log_status", "broken_status",
                                                                   "continuity_status")
        return_json = list(query_set)[0]
        return_json['projectName'] = return_json.pop('project_name')
        return_json['cameraIp'] = return_json.pop('ip')
        return_json['startTime'] = return_json.pop('start_time')
        return_json['startTime'] = localtime(return_json['startTime'])
        return_json['endTime'] = return_json.pop('end_time')
        return_json['endTime'] = localtime(return_json['endTime'])
        return_json['continuityStatus'] = return_json.pop('continuity_status')
        return_json['continuityStatus'] = continuous_running_status(project_pk=pk)['status']
        return_json['logStatus'] = return_json.pop('log_status')
        return_json['logStatus'] = running_status(project_pk=pk)['status']
        return_json['brokenStatus'] = return_json.pop('broken_status')
        return_json['brokenStatus'] = module_running_status(project_pk=pk)[0]
        ProjectSetting.objects.filter(id=pk).update(continuity_status=return_json['continuityStatus'],
                                                    log_status=return_json['logStatus'],
                                                    broken_status=return_json['brokenStatus'])
    else:
        query_set = ProjectSetting.objects.all().values("id", "path", "project_name", "start_time", "log", "delay", "end_time",
                                                     "path_username", "continued", "username", "type", "broken", "owner",
                                                     "prefix_name", "cgi", "password", "path_password", "ip", "log_status", "broken_status",
                                                                   "continuity_status")
        return_json = list(query_set)
        for item_json in return_json:
            item_json['projectName'] = item_json.pop('project_name')
            item_json['cameraIp'] = item_json.pop('ip')
            item_json['startTime'] = item_json.pop('start_time')
            item_json['startTime'] = localtime(item_json['startTime'])
            item_json['endTime'] = item_json.pop('end_time')
            item_json['endTime'] = localtime(item_json['endTime'])
            item_json['continuityStatus'] = item_json.pop('continuity_status')
            item_json['continuity_status'] = continuous_running_status(project_pk=pk)['status']
            item_json['brokenStatus'] = item_json.pop('broken_status')
            item_json['brokenStatus'] = module_running_status(project_pk=pk)[0]
            item_json['logStatus'] = item_json.pop('log_status')
            item_json['logStatus'] = running_status(project_pk=pk)['status']
            ProjectSetting.objects.filter(id=pk).update(continuity_status=item_json['continuityStatus'],
                                                    log_status=item_json['logStatus'],
                                                    broken_status=item_json['brokenStatus'])
    return Response(return_json)

@api_view(['GET'])
@permission_classes((AllowAny,))
def project_counting(requests):
    # total_cam = len(list(ProjectSetting.objects.all()))
    # print('total camera:', total_cam)
    process_id_list = []
    process_list = ProjectSetting.objects.filter(Q(continuity_status='processing') | Q(log_status='processing') |
                                                Q(broken_status='processing'))
    process_cam = process_list.count()
    # print(process_cam)
    for i in process_list:
        process_id_list.append(str(i.id))
    # print(process_id_list)
    process_id = ', '.join(process_id_list)
    return Response({"processingNum":process_cam, 'totalCam':4, 'processingID':process_id})

@api_view(['GET'])
@permission_classes((AllowAny,))
def stop_running_test(requests, pk):
    continue_status, log_status, broken_status = continuous_running_status(project_pk=pk)['status'], running_status(project_pk=pk)['status'], module_running_status(project_pk=pk)[0]
    broken_views.module_stop_detect_periodic_videos(pk)
    continue_views.stop_continuous_test(pk)
    log_views.module_stop_detect_periodic_logs(pk)
    while continue_status == 'processing':
        continue_status = continuous_running_status(project_pk=pk)['status']
        # time.sleep(1)
        print('continue_status stop start')
    while log_status == 'processing':
        log_status = running_status(project_pk=pk)['status']
        # time.sleep(1)
        print('log_status stop start')
    while broken_status == 'processing':
        broken_status = module_running_status(project_pk=pk)[0]
        # time.sleep(1)
        print('broken_status stop start')
    ProjectSetting.objects.filter(id=pk).update(continuity_status=continue_status,
                                                    log_status=log_status,
                                                    broken_status=broken_status)
    print('stop test')
    return Response({"comment": 'Stop current running test'})

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
            create_at = datetime.datetime.strptime(create_at, "%Y%m%d")
        else:
            create_at = re.search('\d{4}\-\d{2}\-\d{2}', dict_item['path']).group(0)
            create_at = datetime.datetime.strptime(create_at, "%Y-%m-%d")
        date_list.append(create_at)
    cnt = collections.Counter()
    for date in date_list:
        cnt[date] += 1
    date_count_dict = dict(cnt)
    for date, count in date_count_dict.items():
        transform_list.append({'createAt': date, 'count': count})
    return transform_list







