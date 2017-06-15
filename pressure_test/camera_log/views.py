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
from camera_log.sd_cycle import SDcycle
from datetime import datetime

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
        sd_locked_file=sd_recording_file_json["sd_locked_file"],
        sd_unlocked_file=sd_recording_file_json["sd_unlocked_file"],
        sd_all_file=sd_recording_file_json["sd_all_file"]
    )

    print(sd_recording_file_json)

    return Response(sd_recording_file_json)

@api_view(['GET'])
@permission_classes((AllowAny,))
def get_camera_log(request):
    time_now = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
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

    # check SD cycle
    former_sd_obj = CameraLog.objects.last()

    if former_sd_obj:
        former_locked_file_list = former_sd_obj.sd_locked_file.split(',')
        former_unlocked_file_list = former_sd_obj.sd_unlocked_file.split(',')

        # former obj is empty string:
        # if former obj is empty string:

        # print("tt")
        # print(len(set(former_locked_file_list)))
        # print(former_locked_file_list))
        # print("yy")




        if len(set(former_locked_file_list)) == 1 and  list(set(former_locked_file_list)) == ['']:
            former_locked_file_list = []
            print("@@@@@@@@@@@@@@")

        if len(set(former_unlocked_file_list)) == 1 and  list(set(former_unlocked_file_list)) == ['']:
            former_unlocked_file_list = []
            print("@@@@@@@@@@@@@@@")




    else:
        former_locked_file_list = []
        former_unlocked_file_list = []


    new_sd_locked_file_list = sd_recording_file_json["sd_locked_file"]
    new_sd_unlocked_file_list = sd_recording_file_json["sd_unlocked_file"]

    print("---------------------")
    print("former_locked_file_list")
    print(former_locked_file_list)
    print("former_unlocked_file_list")
    print(former_unlocked_file_list)
    print("new_sd_locked_file_list")
    print(new_sd_locked_file_list)
    print("new_sd_unlocked_file_list")
    print(new_sd_unlocked_file_list)
    print("--------------------")




    sd_cycle_obj = SDcycle(former_locked_file_list=former_locked_file_list,
                              former_unlocked_file_list=former_unlocked_file_list,
                              new_locked_file_list=new_sd_locked_file_list,
                              new_unlocked_file_list=new_sd_unlocked_file_list)

    sd_cycle_result = sd_cycle_obj.get_result("")
    print("sd_cycle_result:")
    print(sd_cycle_result)



    # check NAS cycle


    # check VAST cycle



    # write db
    CameraLog.objects.create(
        create_at=time_now,
        camera_ip=CAMERA_IP,
        sd_status=sd_status_json["SD_status"],
        sd_used_percent=sd_status_json["SD_used_percent"],
        camera_uptime=my_up_time_json["camera_uptime"],
        camera_cpuloading_average=my_up_time_json["camera_cpuloading_average"],
        camera_cpuloading_idle=my_up_time_json["camera_cpuloading_idle"],
        camera_epoch_time=camera_epoch_time_json["camera_epoch_time"],
        sd_locked_file=','.join(new_sd_locked_file_list),
        sd_unlocked_file=','.join(new_sd_unlocked_file_list),
        sd_all_file=','.join(sd_recording_file_json["sd_all_file"]),
        sd_card_cycling=sd_cycle_result,
    )

    #
    #
    # try:
    #     new_obj = CameraLog.objects.last()     # last object
    #     # print("/////")
    #     # print(new_obj)
    #     # print("++++++")
    #     print(new_obj.id)
    #     print("++-XD- -+++")
    #     print(new_obj.create_at)
    #     # print("//////")
    #
    #     former_obj = CameraLog.objects.get(id=new_obj.id-1)    # former object
    #     # print("former create time")
    #     # print(former_obj.create_at)
    #     # print("former locked file:")
    #     # print(former_obj.locked_file)
    #     # print("former unlocked file:")
    #     # print(former_obj.unlocked_file)
    #     #
    #     # print("new create time")
    #     # print(new_obj.create_at)
    #     # print("new locked file:")
    #     # print(new_obj.locked_file)
    #     # print("new unlocked file:")
    #     # print(new_obj.unlocked_file)
    #
    #     # print("former create time ")
    #     # print(former_obj.create_at)
    #     # print("former locked file:")
    #     # print(former_obj.locked_file.split(','))
    #     # print("former unlocked file:")
    #     # print(former_obj.unlocked_file.split(','))
    #
    #
    #     # former_locked_file_list = former_obj.locked_file.split(',')
    #     # former_unlocked_file_list = former_obj.unlocked_file.split(',')
    #     # new_locked_file_list = former_obj.locked_file.split(',')
    #     # new_unlocked_file_list = former_obj.unlocked_file.split(',')
    #
    #     # print(former_locked_file_list)
    #     # print(former_unlocked_file_list)
    #     # print(new_locked_file_list)
    #     # print(new_unlocked_file_list)
    #
    #     # print(type(former_obj.unlocked_file))
    #     print("hhhhh")
    # except:
    #     print("There isn't former object")
    #     pass
    #
    return Response(camera_log_json)


