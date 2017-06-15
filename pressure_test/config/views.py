# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from config.serializers import ProjectSettingSerializer
from rest_framework import generics
from config.models import ProjectSetting
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from config.models import DefaultSetting
from libs.nas_storage import NasStorage


class ProjectSettingDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProjectSetting.objects.all()
    serializer_class = ProjectSettingSerializer

class ProjectSettingList(generics.ListCreateAPIView):
    queryset = ProjectSetting.objects.all()
    serializer_class = ProjectSettingSerializer

    # def post(self, request, format=None):
    #     print(request.data)

        # return Response("tst")

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
        return_json['endTime'] = return_json.pop('end_time')

    else:
        querry_set = ProjectSetting.objects.all().values("id", "path", "project_name", "start_time", "log", "delay", "end_time",
                                                     "path_username", "continued", "username", "type", "broken", "owner",
                                                     "prefix_name", "cgi", "password", "path_password", "ip")
        return_json = list(querry_set)
        for item_json in return_json:
            item_json['projectName'] = item_json.pop('project_name')
            item_json['cameraIp'] = item_json.pop('ip')
            item_json['startTime'] = item_json.pop('start_time')
            item_json['endTime'] = item_json.pop('end_time')
    return Response(return_json)