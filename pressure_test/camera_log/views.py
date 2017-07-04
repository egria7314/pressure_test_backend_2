
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
# from datetime import datetime
import datetime
from camera_log.libs.timeout import timeout

from threading import Thread
import re
import time
import schedule
import pytz
from threading import Thread
import threading

from libs.vast_storage import VastStorage
from libs.nas_storage import NasStorage
from camera_log.nas_vast_storage_cycle import NasVastCycle
from camera_log.libs.cgi import CGI
from config.models import ProjectSetting
from django.utils.timezone import localtime
from camera_log.libs.monitor import Monitor
from camera_log.nas_vast_storage_cycle import trans_vast_file_to_nas_style

from libs.pressure_test_logging import PressureTestLogging as ptl

TEST_PROJECT_ID = 108 #120    #112  #108
CAMERA_IP = "172.19.16.119"  # support SD
# CAMERA_IP = "172.19.1.39"     # not support SD
CAMERA_USER = "root"
CAMERA_PWD = "12345678z"

NAS_START_DATE = datetime.datetime(2000, 6, 3, 0, 0, 0)

VAST_TEST_STARTDATE = datetime.datetime(2017, 6, 25, 0, 0, 0)

GLOBAL_TIMEOUT = 3000   # default timeout


# def job():
#     print("I'm working...")
#     # req = urllib.request.Request('http://172.19.16.133:8000/camera_log/')
#     # http = urllib3.PoolManager()
#     # http.request('GET', 'http://172.19.16.133:8000/camera_log/')


# check sd support
def support_sd(username, password, ip, cgi_command, timeout=300):
    support = True
    # sd_support_cgi_result = CGI().get_cgi("root", "12345678z", "172.19.16.119", "capability_supportsd")    # sd support
    sd_support_cgi_result = CGI().get_cgi(username, password, ip, cgi_command, timeout=timeout)    # sd not support


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

    return Response(sd_status_json)


@api_view(['GET'])
@permission_classes((AllowAny,))
def get_up_time(requests):
    # camera_ip = "172.19.16.119"
    # camera_user = "root"
    # camera_pwd = "12345678z"

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


# def test_run_camera_thread(project_id):
#     th = Thread(target=run_camera_schedule, args=(project_id,))
#     th.start()
##


@api_view(['GET'])
@permission_classes((AllowAny,))
def test_camera(request):
    run_cameralog_schedule_by_id(TEST_PROJECT_ID)
    # set_camera_log(69)


    return Response({'status: ': 'ok'})

def run_cameralog_schedule_by_id(project_id):
    # test_run_camera_thread(1)
    from camera_log.libs import monitor
    ptl.logging_info('[Info] Run camera log schedule by ID.')

    task_camera_obj = ProjectSetting.objects.get(id=project_id)

    need_log_bool = task_camera_obj.log
    print("LOG STATUS!!!")
    print(need_log_bool)
    if need_log_bool:
        start_time = localtime(task_camera_obj.start_time)
        end_time = localtime(task_camera_obj.end_time)
        now_time = datetime.datetime.now(pytz.timezone('Asia/Taipei'))

        interval_time = datetime.timedelta(hours=1)
        # interval_time = datetime.timedelta(minutes=2)

        periodic_check_points = []
        periodic_time = start_time

        if (end_time < now_time):
            print("End < NOW ")
            end_time = now_time
            periodic_time = now_time
        elif (start_time < now_time):
            print("START < NOW")
            periodic_time = now_time

        while periodic_time < end_time:
            periodic_check_points.append(periodic_time)
            periodic_time += interval_time
        periodic_check_points.append(end_time)

        print("periodic points: ", periodic_check_points)
        m = Monitor()
        for periodic_time in periodic_check_points:
            m.add_periodic_jobs(
                time.mktime(periodic_time.timetuple()),
                set_camera_log,(project_id, start_time)
             )
        m.start()

        ########ori
        #
        # periodic_check_points = []
        # while start_time < end_time:
        #     periodic_check_points.append(start_time)
        #     start_time += interval_time
        # periodic_check_points.append(end_time)
        # m = Monitor()
        # # start_time_periodic_check_points = periodic_check_points[:-1]
        # # end_time_periodic_check_points = periodic_check_points[1:]
        #
        # for checkpoint in periodic_check_points:
        #     m.add_periodic_jobs(
        #         time.mktime(checkpoint.timetuple()),
        #         set_camera_log,(project_id, start_time)
        #     )
        # m.start()
        # ori!!!!!!


        monitor.camera_id_2_monitor[str(project_id)] = m
        print("monitor: ", monitor.camera_id_2_monitor)

    return Response({'message': "Insert camera into schedule successfully", 'project_id': project_id })



@api_view(['GET'])
@permission_classes((AllowAny,))
def test_camera_status(request):
    res = running_status(TEST_PROJECT_ID)

    return Response(res)


def running_status(project_pk):
    from camera_log.libs import monitor
    ptl.logging_info('[Info] Run camera log schedule by ID.')

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


    return {'status': status, 'size': queue_size, 'next schedule': next_schedule}

@api_view(['GET'])
@permission_classes((AllowAny,))
def test_stop_camera_logs(request):
    stop_detect_periodic_logs(TEST_PROJECT_ID)
    return Response({'status:': 'OK'})


def stop_detect_periodic_logs(project_id):
    ret = module_stop_detect_periodic_logs(project_id)
    return ret


def module_stop_detect_periodic_logs(project_id):
    from camera_log.libs import monitor
    ptl.logging_info('[Info] Stop camera log schedule by ID.')
    # get project object

    print("Kill project ids:")
    print(monitor.camera_id_2_monitor.keys())
    print("***")

    if str(project_id) in monitor.camera_id_2_monitor.keys():
        m = monitor.camera_id_2_monitor[str(project_id)]
        m.stop()

    ret = {'message': "Cancel camera from schedule successfully"}
    return ret


# # OK!!
# def test_run_camera_thread(project_id):
#     th = Thread(target=run_camera_schedule, args=(project_id,))
#     th.start()

#
#
# def run_camera_schedule(project_id):
#     result = {}
#     schedule.every().minute.do(set_camera_log, project_id)
#
#     while True:
#         try:
#             result["status"] = "OK"
#             schedule.run_pending()
#             # print(schedule.jobs)
#             # time.sleep(1)
#
#         except BaseException as e:
#             result["status"] = "Schedule Unknown Fail"
#             print(e)



@api_view(['GET'])
@permission_classes((AllowAny,))
def test_set_camera_api(request):

    task_camera_obj = ProjectSetting.objects.get(id=TEST_PROJECT_ID)

    start_time = localtime(task_camera_obj.start_time)
    set_camera_log(TEST_PROJECT_ID, start_time)


    ##### test of carlos ####
    # start_time = localtime(task_camera_obj.start_time)
    # timestamp_end = datetime.datetime.now(pytz.timezone('Asia/Taipei'))


    # print("START")
    # print(start_time)
    # print("END")
    # print(timestamp_end)
    # vs=VastStorage()
    # clips = vs.get_video_vast('autotest', 'autotest', '', '//172.19.11.189/Public/autotest/steven/VAST/2017-06-26/4-FD816B-HT', start_time, timestamp_end)
    # print ("*******************")
    # print (clips)
    # print ("******************")
    # return Response(' : '.join(sorted(clips)))
    ##### test of carlos ####


    ###### TIMEOUT TEST  #########
    # try:
    #
    #     # print(mytest())
    #     global TIMEOUT
    #     TIMEOUT = 1
    #
    #
    #     test = mytest()
    #     print(test)
    # except Exception as e:
    #     print("EXCEPT!!!!!")
    #     print(e)


    return Response({'status:': 'OK'})

# def glob(new_time):
#     global TIMEOUT
#     TIMEOUT = new_time
#     return True

# @timeout(TIMEOUT)
def mytest():

    mytest = timeout(GLOBAL_TIMEOUT)

    print("Start!!!!")

    num = 0
    num_add = num + 1

    time.sleep(5)

    return str(threading.current_thread()) + ": " + str(num) + str(GLOBAL_TIMEOUT)


@api_view(['GET'])
@permission_classes((AllowAny,))
def get_schedule_status(request):
    jobs_status = {}
    # print(schedule.jobs)
    jobs_status["job_status"] = str(schedule.jobs)

    return Response(jobs_status)


def set_camera_log(project_id, start_time):
    ptl.logging_info('[Info] Set camera log is working ...')
    print("****************************")
    print("Set camera log is working....")

    ###########
    camera_log_json = {}
    time_now = datetime.datetime.now()
    camera_log_json["createAt"] = time_now

    # get camera info by id ()
    task_camera_obj = ProjectSetting.objects.get(id=project_id)         # id now is temp, will get POST from Leo
    global GLOBAL_TIMEOUT
    GLOBAL_TIMEOUT = task_camera_obj.cgi
    timeout = task_camera_obj.cgi
    print("****")
    print(task_camera_obj.prefix_name)
    print("*****")

    camera_ip = task_camera_obj.ip
    camera_user = task_camera_obj.username
    camera_password = task_camera_obj.password
    storage_path = task_camera_obj.path
    storage_user = task_camera_obj.path_username
    storage_password = task_camera_obj.path_password


    final_camera_log_json = {}
    final_camera_log_json["id"] = project_id    # temp
    all_data_list = []
    PREFIX = task_camera_obj.prefix_name   # temp

    # up time
    my_up_time_json = {}
    try:
        ptl.logging_info('[Info] Set uptime.')
        my_up_time_json = set_up_time(camera_ip, camera_user, camera_password, timeout)
        camera_log_json.update(my_up_time_json)
    except Exception as e:
        ptl.logging_error('[Exception] set uptime error, [Error msg]:{0}'.format(e))
        print(e)
        my_up_time_json["uptime"] = "Fail/Timeout"
        my_up_time_json["loadAverage"] = "Fail/Timeout"
        my_up_time_json["idle"] = "Fail/Timeout"


    # # epoch time
    # ptl.logging_info('[Info] Set epoch time.')
    # camera_epoch_time = Epochtime(camera_ip, camera_user, camera_password)
    # camera_epoch_time_json = camera_epoch_time.get_result()
    # camera_log_json.update(camera_epoch_time_json)

    # sd related
    # first check sd support
    sd_support = support_sd(camera_user, camera_password, camera_ip, "capability_supportsd", timeout)
    sd_status_json = {}

    if sd_support:
        # sd status
        try:
            ptl.logging_info('[Info] Set sd status.')
            sd_status_json = set_sd_status(camera_ip, camera_user, camera_password, timeout)
            camera_log_json.update(sd_status_json)
        except Exception as e:
            ptl.logging_error('[Exception] set sd status error, [Error msg]:{0}'.format(e))
            print(e)
            sd_status_json["sdCardStatus"] = "Fail/Timeout"
            sd_status_json["sdCardUsed"] = "Fail/Timeout"


        # sd recording file
        new_sd_locked_file_list = []
        new_sd_unlocked_file_list = []
        try:
            ptl.logging_info('[Info] Set sd recording files.')
            new_sd_locked_file_str, new_sd_unlocked_file_str, new_sd_all_file_str, \
            new_sd_locked_file_list, new_sd_unlocked_file_list = set_sd_recording_files(camera_ip, camera_user, camera_password, PREFIX, timeout)
        except Exception as e:
            ptl.logging_error('[Exception] set sd recording file error, [Error msg]:{0}'.format(e))
            print(e)
            new_sd_locked_file_str = "Fail/Timeout"
            new_sd_unlocked_file_str = "Fail/Timeout"
            new_sd_all_file_str = "Fail/Timeout"
            new_sd_locked_file_list.append("Fail/Timeout")
            new_sd_unlocked_file_list.append("Fail/Timeout")


        # check SD cycle #
        try:
            ptl.logging_info('[Info] Set sd cycle.')
            sd_cycle_result, sd_cycle_json = set_sd_cycle(project_id, new_sd_locked_file_list, new_sd_unlocked_file_list, PREFIX)
            camera_log_json.update(sd_cycle_json)
        except Exception as e:
            ptl.logging_error('[Exception] set sd cycle error, [Error msg]:{0}'.format(e))
            print(e)
            sd_cycle_result = "Fail/Timeout"


    else:
        comment = "Not Support"
        sd_status_json["sdCardStatus"] = comment
        sd_status_json["sdCardUsed"] = comment
        new_sd_locked_file_str = comment
        new_sd_unlocked_file_str = comment
        new_sd_all_file_str = comment
        sd_cycle_result = comment


    # storage cycle
    new_nas_file_list = []
    new_vast_file_list = []
    nas_cycle_result=""
    vast_cycle_result=""
    medium_or_high = task_camera_obj.type

    try:
        if medium_or_high.lower() == "high":
            ptl.logging_info('[Info] Set high pressure storage cycle.')
            new_nas_file_list, nas_cycle_result = get_storagefile_and_cycle(project_id, task_camera_obj, "NAS", NAS_START_DATE)
        # medium (by VAST)
        else:
            ptl.logging_info('[Info] Set medium pressure storage cycle.')
        # ####################### VAST ################################
        # #check VAST cycle
            new_vast_file_list, vast_cycle_result = get_storagefile_and_cycle(project_id, task_camera_obj, "VAST", start_time)
    except Exception as e:
        ptl.logging_error('[Exception] set storage cycle error, [Error msg]:{0}'.format(e))
        nas_cycle_result = "Fail/Timeout"
        vast_cycle_result = "Fail/Timeout"
        new_nas_file_list.append("Fail/Timeout")
        new_vast_file_list.append("Fail/Timeout")


    print("create DB:")
    # write db
    CameraLog.objects.create(
        project_id=project_id,
        create_at=time_now,
        camera_ip=camera_ip,
        sd_status=sd_status_json["sdCardStatus"],
        sd_used_percent=sd_status_json["sdCardUsed"],
        camera_uptime=my_up_time_json["uptime"],
        camera_cpuloading_average=my_up_time_json["loadAverage"],
        camera_cpuloading_idle=my_up_time_json["idle"],
        # camera_epoch_time=camera_epoch_time_json["camera_epoch_time"],
        sd_locked_file=new_sd_locked_file_str,
        sd_unlocked_file=new_sd_unlocked_file_str,
        sd_all_file=new_sd_all_file_str,
        sd_card_cycling=sd_cycle_result,

        nas_file=','.join(new_nas_file_list),
        nas_cycling=nas_cycle_result,

        vast_file=','.join(new_vast_file_list),
        vast_cycling=vast_cycle_result,
    )

    all_data_list.append(camera_log_json)
    final_camera_log_json["data"] = all_data_list

# @timeout(GLOBAL_TIMEOUT)
def set_up_time(camera_ip, camera_user, camera_password, timeout=300):
    my_up_time = Uptime(camera_ip, camera_user, camera_password)
    my_up_time_json = my_up_time.get_result(timeout)

    return my_up_time_json

# @timeout(GLOBAL_TIMEOUT)
def set_sd_status(camera_ip, camera_user, camera_password, timeout=300):
    print("***TEST TIMEOUT***")
    print(GLOBAL_TIMEOUT)


    my_sd_status = SDstatus(camera_ip, camera_user, camera_password)
    sd_status_json = my_sd_status.get_result(timeout)

    return sd_status_json

# @timeout(GLOBAL_TIMEOUT)
def set_sd_recording_files(camera_ip, camera_user, camera_password, PREFIX, timeout=300):
    new_sd_locked_file_str = ""
    new_sd_unlocked_file_str = ""
    new_sd_all_file_str = ""
    new_sd_locked_file_list = []
    new_sd_unlocked_file_list = []

    sd_recording_file = Sdrecordingfile(camera_ip, camera_user, camera_password)
    sd_recording_file_json = sd_recording_file.get_fw_file_dict(timeout)
    new_sd_locked_file_list = [file for file in sd_recording_file_json["sd_locked_file"] if PREFIX in file]


    new_sd_locked_file_str = ','.join(new_sd_locked_file_list)

    new_sd_unlocked_file_list = [file for file in sd_recording_file_json["sd_unlocked_file"] if PREFIX in file]


    new_sd_unlocked_file_str = ','.join(new_sd_unlocked_file_list)
    new_sd_all_file_str = ','.join([file for file in sd_recording_file_json["sd_all_file"] if PREFIX in file])

    return new_sd_locked_file_str, new_sd_unlocked_file_str, new_sd_all_file_str, \
           new_sd_locked_file_list, new_sd_unlocked_file_list

# @timeout(GLOBAL_TIMEOUT)
def set_sd_cycle(project_id, new_sd_locked_file_list, new_sd_unlocked_file_list, PREFIX):

    try:
        former_cam_obj = CameraLog.objects.filter(project_id=project_id).order_by('-id')[0]
        former_sd_locked_file_list = former_cam_obj.sd_locked_file.split(',')
        former_sd_unlocked_file_list = former_cam_obj.sd_unlocked_file.split(',')
        former_sd_locked_file_list = check_list(former_sd_locked_file_list)
        former_sd_unlocked_file_list = check_list(former_sd_unlocked_file_list)

    except Exception as e:
        ptl.logging_warning('[Exception] Did not find former camera obj of same project id, [Error msg]:{0}'.format(e))
        former_sd_locked_file_list = []
        former_sd_unlocked_file_list = []


    # former_cam_obj = CameraLog.objects.filter(project_id=project_id).order_by('-id')[0]
    #
    # if former_cam_obj:
    #     former_sd_locked_file_list = former_cam_obj.sd_locked_file.split(',')
    #     former_sd_unlocked_file_list = former_cam_obj.sd_unlocked_file.split(',')
    #     former_sd_locked_file_list = check_list(former_sd_locked_file_list)
    #     former_sd_unlocked_file_list = check_list(former_sd_unlocked_file_list)
    # else:
    #     print("***TEST999****")
    #     former_sd_locked_file_list = []
    #     former_sd_unlocked_file_list = []

    sd_cycle_obj = SDcycle(former_locked_file_list=former_sd_locked_file_list,
                              former_unlocked_file_list=former_sd_unlocked_file_list,
                              new_locked_file_list=new_sd_locked_file_list,
                              new_unlocked_file_list=new_sd_unlocked_file_list)

    sd_cycle_result = sd_cycle_obj.get_result(PREFIX)
    print("sd_cycle_result:")
    print(sd_cycle_result)
    sd_cycle_json = {}
    sd_cycle_json["sdCardCycling"] = sd_cycle_result

    return sd_cycle_result, sd_cycle_json



# @timeout(GLOBAL_TIMEOUT)
def get_storagefile_and_cycle(project_id, task_camera_obj, storage_by, start_time):
######################## NAS #################################
    # check NAS cycle
    storage_path = task_camera_obj.path
    storage_user = task_camera_obj.path_username
    storage_password = task_camera_obj.path_password
    PREFIX = task_camera_obj.prefix_name
    new_storage_file_list = []
    storage_cycle_result=""

    try:
        ptl.logging_info('[Info] Get former storage object.')
        # get the latest obj of same project id
        former_cam_obj = CameraLog.objects.filter(project_id=project_id).order_by('-id')[0]
        if storage_by == "NAS":
            former_storage_file_list = former_cam_obj.nas_file.split(',')
        elif storage_by == "VAST":
            former_storage_file_list = former_cam_obj.vast_file.split(',')

        former_storage_file_list = check_list(former_storage_file_list)
    except Exception as e:
        ptl.logging_warning('[Exception] Did not find former camera obj of same project id when getting storage '
                                  'cycle, [Error msg]:{0}'.format(e))
        former_storage_file_list=[]

    finally:

        try:
            timestamp_end = datetime.datetime.now(pytz.timezone('Asia/Taipei'))

            sudo_password = 'fftbato'
            storage_files_dict = []

            if storage_by == "NAS":
                timestamp_start = start_time
                test_nas_obj = NasStorage(storage_user, storage_password)
                storage_path = storage_path.replace('\\','/')
                storage_files_dict = test_nas_obj.get_video_nas(storage_user, storage_password, sudo_password, storage_path,
                                                         PREFIX, timestamp_start, timestamp_end)

                print("*****GET NAS FILE******")
                print(storage_files_dict)


                storage_files_list = list(storage_files_dict.keys())
                new_storage_file_list = []
                for nas_file in storage_files_list:
                    print("NAS FILE*")
                    print(nas_file)
                    print("storage PATH")
                    print(storage_path)

                    if storage_path.endswith('/'):
                        end_index = nas_file.find(storage_path) + len(storage_path)
                    else:
                        end_index = nas_file.find(storage_path) + len(storage_path) + 1
                    new_storage_file_list.append(nas_file[end_index:])

                nas_cycle_obj = NasVastCycle(former_file_list=former_storage_file_list,
                                           new_file_list=new_storage_file_list)
                storage_cycle_result = nas_cycle_obj.get_result(PREFIX)

            elif storage_by == "VAST":
                timestamp_start = start_time
                test_vast_obj = VastStorage(storage_user, storage_password)
                storage_path = storage_path.replace('\\','/')
                storage_files_dict = test_vast_obj.get_video_vast(storage_user, storage_password, '', storage_path, timestamp_start, timestamp_end)

                # print("****VAST FILE:****")
                # print(storage_files_dict)

                vast_files_list = list(storage_files_dict.keys())

                for vast_file in vast_files_list:
                        end_index = vast_file.rfind('/')
                        new_storage_file_list.append(vast_file[end_index+1:])


                new_storage_file_list = trans_vast_file_to_nas_style(new_storage_file_list)
                cycle_obj = NasVastCycle(former_file_list=former_storage_file_list,
                                           new_file_list=new_storage_file_list)

                storage_cycle_result = cycle_obj.get_result()

        except Exception as e:
            ptl.logging_error('[Exception] NAS/VAST get files Fail! or Timeout, [Error msg]:{0}'.format(e))
            print("NAS/VAST get files Fail! or Timeout")
            print(e)


    return new_storage_file_list, storage_cycle_result




def check_list(file_list):
    empty_list = file_list
    if len(set(file_list)) == 1 and  list(set(file_list)) == ['']:
            empty_list = []

    return empty_list


@api_view(['GET'])
@permission_classes((AllowAny,))
def get_all_camera_log(request, pi=None):
    ptl.logging_info('[Info] Get all camera log API.')
    # ptl.logging_info('hello log')
    project_id = pi

    final_camera_log_json = {}
    final_camera_log_json["id"] = project_id
    data_list = []

    all_camera_logs = CameraLog.objects.filter(project_id=project_id)
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




