
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
import re
import time
import schedule

from libs.vast_storage import VastStorage
from libs.nas_storage import NasStorage
from camera_log.nas_vast_storage_cycle import NasVastCycle
from camera_log.libs.cgi import CGI
from config.models import ProjectSetting


CAMERA_IP = "172.19.16.119"  # support SD
# CAMERA_IP = "172.19.1.39"     # not support SD
CAMERA_USER = "root"
CAMERA_PWD = "12345678z"


# def job():
#     print("I'm working...")
#     # req = urllib.request.Request('http://172.19.16.133:8000/camera_log/')
#     # http = urllib3.PoolManager()
#     # http.request('GET', 'http://172.19.16.133:8000/camera_log/')


# check sd support
def support_sd(username, password, ip, cgi_command):
    support = True
    # sd_support_cgi_result = CGI().get_cgi("root", "12345678z", "172.19.16.119", "capability_supportsd")    # sd support
    sd_support_cgi_result = CGI().get_cgi(username, password, ip, cgi_command)    # sd not support


    m = re.match(r"(.*)=\'(.*)\'", sd_support_cgi_result)
    print(m.group(2))

    if m.group(2) == "0":
        support = False

    return support


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
        sd_status=sd_status_json["sdCardStatus"],
        sd_used_percent=sd_status_json["sdCardUsed"],
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
        camera_uptime=my_up_time_json["uptime"],
        camera_cpuloading_average=my_up_time_json["loadAverage"],
        camera_cpuloading_idle=my_up_time_json["idle"],
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

    # print(sd_recording_file_json)

    return Response(sd_recording_file_json)


@api_view(['GET'])
@permission_classes((AllowAny,))
def run_camera_schedule(request):
    result = {}
    schedule.every().minute.do(set_camera_log, 17)

    while True:
        try:
            result["status"] = "OK"
            schedule.run_pending()
            # print(schedule.jobs)
            # time.sleep(1)

        except BaseException as e:
            result["status"] = "Schedule Unknown Fail"
            print(e)

    return Response(result)

@api_view(['GET'])
@permission_classes((AllowAny,))
def get_schedule_status(request):
    jobs_status = {}
    # print(schedule.jobs)
    jobs_status["job_status"] = str(schedule.jobs)

    return Response(jobs_status)


# @api_view(['GET'])
# @permission_classes((AllowAny,))
# def set_camera_log(request):
def set_camera_log(projectid):
    print("*****************************")
    print("Set camera log is working....")
    print(schedule.jobs)

    ############
    camera_log_json = {}
    time_now = datetime.now().strftime('%Y%m%d %H:%M:%S')
    camera_log_json["createAt"] = time_now

    # get camera info by id ()
    task_camera_obj = ProjectSetting.objects.get(id=projectid)         # id now is temp, will get POST from Leo
    print("*****")
    print(task_camera_obj.prefix_name)
    print("****")

    camera_ip = task_camera_obj.ip
    camera_user = task_camera_obj.username
    camera_password = task_camera_obj.password

    storage_path = task_camera_obj.path
    storage_user = task_camera_obj.path_username
    storage_password = task_camera_obj.path_password


    final_camera_log_json = {}
    final_camera_log_json["id"] = "1"    # temp
    all_data_list = []
    PREFIX = task_camera_obj.prefix_name   # temp

    # up time
    my_up_time = Uptime(camera_ip, camera_user, camera_password)
    my_up_time_json = my_up_time.get_result()
    camera_log_json.update(my_up_time_json)

    # epoch time
    camera_epoch_time = Epochtime(camera_ip, camera_user, camera_password)
    camera_epoch_time_json = camera_epoch_time.get_result()
    camera_log_json.update(camera_epoch_time_json)

    # sd related
    # first check sd support
    sd_support = support_sd(camera_user, camera_password, camera_ip, "capability_supportsd")
    sd_status_json = {}

    if sd_support:
        # sd status
        my_sd_status = SDstatus(camera_ip, camera_user, camera_password)
        sd_status_json = my_sd_status.get_result()
        camera_log_json.update(sd_status_json)

        # sd recording file
        sd_recording_file = Sdrecordingfile(camera_ip, camera_user, camera_password)
        sd_recording_file_json = sd_recording_file.get_fw_file_dict()
        new_sd_locked_file_list = sd_recording_file_json["sd_locked_file"]
        new_sd_locked_file_str = ','.join(new_sd_locked_file_list)
        new_sd_unlocked_file_list = sd_recording_file_json["sd_unlocked_file"]
        new_sd_unlocked_file_str = ','.join(new_sd_unlocked_file_list)
        new_sd_all_file_str = ','.join(sd_recording_file_json["sd_all_file"])


        # camera_log_json.update(sd_recording_file_json)

        # check SD cycle
        former_cam_obj = CameraLog.objects.last()

        if former_cam_obj:
            former_sd_locked_file_list = former_cam_obj.sd_locked_file.split(',')
            former_sd_unlocked_file_list = former_cam_obj.sd_unlocked_file.split(',')
            former_sd_locked_file_list = check_list(former_sd_locked_file_list)
            former_sd_unlocked_file_list = check_list(former_sd_unlocked_file_list)
        else:
            former_sd_locked_file_list = []
            former_sd_unlocked_file_list = []

        sd_cycle_obj = SDcycle(former_locked_file_list=former_sd_locked_file_list,
                                  former_unlocked_file_list=former_sd_unlocked_file_list,
                                  new_locked_file_list=new_sd_locked_file_list,
                                  new_unlocked_file_list=new_sd_unlocked_file_list)

        sd_cycle_result = sd_cycle_obj.get_result(PREFIX)
        print("sd_cycle_result:")
        print(sd_cycle_result)
        sd_cycle_json = {}
        sd_cycle_json["sdCardCycling"] = sd_cycle_result
        camera_log_json.update(sd_cycle_json)
    else:
        comment = "Not Support"
        sd_status_json["sdCardStatus"] = comment
        sd_status_json["sdCardUsed"] = comment
        new_sd_locked_file_str = comment
        new_sd_unlocked_file_str = comment
        new_sd_all_file_str = comment
        sd_cycle_result = comment


    medium_or_high = task_camera_obj.type
    if medium_or_high.lower() == "high":
        ######################## To Do ################################
        # check NAS cycle
        new_nas_file_list = []
        nas_cycle_result=""

        former_cam_obj = CameraLog.objects.last()

        if former_cam_obj:
            former_nas_file_list = former_cam_obj.nas_file.split(',')
            former_nas_file_list = check_list(former_nas_file_list)
        else:
            former_nas_file_list=[]

        try:
            timestamp_nas_start = datetime(2000, 6, 3, 0, 0, 0)
            timestamp_nas_end = datetime.now()
            nas_sudo_password = 'fftbato'

            test_vast_obj = NasStorage(storage_user, storage_password)
            # print(test_vast_obj)
            # nas_path = '\\\\172.19.11.189\\Public\\autotest\\steven'.replace('\\','/')
            nas_path = storage_path.replace('\\','/')

            nas_files_dict = test_vast_obj.get_video_nas(storage_user, storage_password, nas_sudo_password, nas_path,
                                                         PREFIX, timestamp_nas_start, timestamp_nas_end)

            nas_files_list = list(nas_files_dict.keys())
            new_nas_file_list = []
            for nas_file in nas_files_list:
                end_index = nas_file.find(nas_path) + len(nas_path) + 1
                new_nas_file_list.append(nas_file[end_index:])

            nas_cycle_obj = NasVastCycle(former_file_list=former_nas_file_list,
                                       new_file_list=new_nas_file_list)
            nas_cycle_result = nas_cycle_obj.get_result(PREFIX)
        except:
            print("NAS get files Fail! or Timeout")


    # medium (by VAST)
    else:
    # ####################### To Do ################################
    # #check VAST cycle
        try:
            timestamp_vast_start = datetime(2017, 6, 2, 0, 0, 0)
            timestamp_vast_end = datetime.now()
            # print(end_datetime_object)

            test_vast_obj = VastStorage(storage_user, storage_password)
            path = storage_path.replace('\\','/')
            vast_files_dict = test_vast_obj.get_video_vast(storage_user, storage_password, '', path, timestamp_vast_start, timestamp_vast_end)
            print(vast_files_dict)

            vast_files_list = list(vast_files_dict.keys())
            print("VAST!!!!")
            print(vast_files_list)
        except:
            print("VAST get files Fail! or Timeout")

    ####################### To Do ################################

    # write db
    CameraLog.objects.create(
        create_at=time_now,
        camera_ip=CAMERA_IP,
        sd_status=sd_status_json["sdCardStatus"],
        sd_used_percent=sd_status_json["sdCardUsed"],
        camera_uptime=my_up_time_json["uptime"],
        camera_cpuloading_average=my_up_time_json["loadAverage"],
        camera_cpuloading_idle=my_up_time_json["idle"],
        camera_epoch_time=camera_epoch_time_json["camera_epoch_time"],
        sd_locked_file=new_sd_locked_file_str,
        sd_unlocked_file=new_sd_unlocked_file_str,
        sd_all_file=new_sd_all_file_str,
        sd_card_cycling=sd_cycle_result,

        nas_file=','.join(new_nas_file_list),
        nas_cycling=nas_cycle_result
    )

    all_data_list.append(camera_log_json)
    final_camera_log_json["data"] = all_data_list


    return final_camera_log_json
    # return Response(final_camera_log_json)

def check_list(file_list):
    empty_list = file_list
    if len(set(file_list)) == 1 and  list(set(file_list)) == ['']:
            empty_list = []

    return empty_list


@api_view(['GET'])
@permission_classes((AllowAny,))
def get_all_camera_log(request):
    final_camera_log_json = {}
    final_camera_log_json["id"] = "1"
    data_list = []

    all_camera_logs = CameraLog.objects.all()
    for log_obj in all_camera_logs:
        log_data_dict = {}
        log_data_dict["createAt"] = log_obj.create_at
        log_data_dict["uptime"] = log_obj.camera_uptime
        log_data_dict["idle"] = log_obj.camera_cpuloading_idle
        log_data_dict["loadAverage"] = log_obj.camera_cpuloading_average
        log_data_dict["sdCardStatus"] = log_obj.sd_status
        log_data_dict["sdCardUsed"] = log_obj.sd_used_percent
        log_data_dict["sdCardCycling"] = log_obj.sd_card_cycling
        log_data_dict["nasCycling"] = log_obj.nas_cycling
        log_data_dict["vastCycling"] = log_obj.vast_cycling

        data_list.append(log_data_dict)

        # print(log_obj.create_at)

    final_camera_log_json["data"] = data_list

    return Response(final_camera_log_json)




