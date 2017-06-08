from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated

# from pressure_test.camera_log.sd_status import SDstatus
from camera_log.sd_status import SDstatus
from camera_log.models import SdStatus
from camera_log.uptime import Uptime
from camera_log.models import UpTime
from camera_log.epoch_time import Epochtime
from camera_log.models import EpochTime
from camera_log.sd_recording_file import Sdrecordingfile
from camera_log.models import SdRecordingFile

from camera_log.models import CameraLog
import json


CAMERA_IP = "172.19.16.119"
CAMERA_USER = "root"
CAMERA_PWD = "12345678z"


# Create your views here.

@api_view(['GET'])
@permission_classes((AllowAny,))
def get_sd_status(requests):
    # CAMERA_IP = "172.19.16.119"
    # CAMERA_USER = "root"
    # CAMERA_PWD = "12345678z"

    my_sd_status = SDstatus(CAMERA_IP, CAMERA_USER, CAMERA_PWD)
    sd_status_json = my_sd_status.get_result()

    # my_up_time = Uptime(camera_ip, camera_user, camera_pwd)
    # my_up_time_json = my_up_time.get_result()



    SdStatus.objects.create(
        camera_ip=CAMERA_IP,
        sd_status=sd_status_json["SD_status"],
        sd_used_percent=sd_status_json["SD_used_percent"],
    )

    # print(my_up_time)

    # UpTime.objects.create(
    #     camera_uptime=
    #
    # )
    #

    # data = requests.data
    # username = data.get('username')
    # password = data.get('password')
    #
    # try:
    #     # payload = {
    #     #     'username': username,
    #     #     'password': password
    #     # }
    #     # login_url = 'http://172.19.16.51:8881/jarvis-auth/auth_and_obtain_jwt_token'
    #     # r = req.post(login_url, data=payload)
    #     # print(r.text)
    #     # res_json = json.loads(r.text)
    #
    #     # requests.post( )
    # except Exception as e:
    #     print(e)

    return Response(sd_status_json)


@api_view(['GET'])
@permission_classes((AllowAny,))
def get_up_time(requests):
    # camera_ip = "172.19.16.119"
    # camera_user = "root"
    # camera_pwd = "12345678z"
    #
    my_up_time = Uptime(CAMERA_IP, CAMERA_USER, CAMERA_PWD)
    my_up_time_json = my_up_time.get_result()

    UpTime.objects.create(
        camera_uptime=my_up_time_json["camera_uptime"],
        camera_cpuloading_average=my_up_time_json["camera_cpuloading_average"],
        camera_cpuloading_idle=my_up_time_json["camera_cpuloading_idle"],
    )

    return Response(my_up_time_json)

@api_view(['GET'])
@permission_classes((AllowAny,))
def get_epoch_time(requests):
    camera_epoch_time = Epochtime(CAMERA_IP, CAMERA_USER, CAMERA_PWD)
    camera_epoch_time_json = camera_epoch_time.get_result()

    EpochTime.objects.create(
        camera_epoch_time=camera_epoch_time_json["camera_epoch_time"]
    )

    return Response(camera_epoch_time_json)

@api_view(['GET'])
@permission_classes((AllowAny,))
def get_sd_recording_file(request):
    sd_recording_file = Sdrecordingfile(CAMERA_IP, CAMERA_USER, CAMERA_PWD)
    sd_recording_file_json = sd_recording_file.get_fw_file_dict()

    SdRecordingFile.objects.create(
        locked_file=sd_recording_file_json["locked_file"],
        unlocked_file=sd_recording_file_json["unlocked_file"],
        all_file=sd_recording_file_json["all_file"]
    )

    print(sd_recording_file_json)

    return Response(sd_recording_file_json)

@api_view(['GET'])
@permission_classes((AllowAny,))
def get_camera_log(request):
    # sd status
    my_sd_status = SDstatus(CAMERA_IP, CAMERA_USER, CAMERA_PWD)
    sd_status_json = my_sd_status.get_result()

    # up time
    my_up_time = Uptime(CAMERA_IP, CAMERA_USER, CAMERA_PWD)
    my_up_time_json = my_up_time.get_result()

    # epoch time
    camera_epoch_time = Epochtime(CAMERA_IP, CAMERA_USER, CAMERA_PWD)
    camera_epoch_time_json = camera_epoch_time.get_result()

    # sd recording file
    sd_recording_file = Sdrecordingfile(CAMERA_IP, CAMERA_USER, CAMERA_PWD)
    sd_recording_file_json = sd_recording_file.get_fw_file_dict()

    camera_log_json = {}
    camera_log_json.update(sd_status_json)
    camera_log_json.update(my_up_time_json)
    camera_log_json.update(camera_epoch_time_json)
    camera_log_json.update(sd_recording_file_json)


    CameraLog.objects.create(
        camera_ip=CAMERA_IP,
        sd_status=sd_status_json["SD_status"],
        sd_used_percent=sd_status_json["SD_used_percent"],
        camera_uptime=my_up_time_json["camera_uptime"],
        camera_cpuloading_average=my_up_time_json["camera_cpuloading_average"],
        camera_cpuloading_idle=my_up_time_json["camera_cpuloading_idle"],
        camera_epoch_time=camera_epoch_time_json["camera_epoch_time"],
        locked_file=sd_recording_file_json["locked_file"],
        unlocked_file=sd_recording_file_json["unlocked_file"],
        all_file=sd_recording_file_json["all_file"],
    )

    return Response(camera_log_json)




