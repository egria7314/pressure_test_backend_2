__author__ = 'carlos.hu'
from camera_log.telnet_module import TelnetModule
from camera_log.models import CameraLog
import re
import json
from libs.pressure_test_logging import PressureTestLogging as ptl
import socket

class Uptime(object):
    def __init__(self, ip, account, password):
        """
        Keyword arguments:
        ip -- the string of ip that is camera ip
        account -- the string of account that is camera account
        password -- the string of password that is camera password
        """
        self.ip = ip
        self.account = account
        self.password = password

    def find_last_valid_uptime(self, project_id):
        former_cam_objs = CameraLog.objects.filter(project_id=project_id).order_by('-id')
        for o in former_cam_objs:
            if self.__get_up_time_content(o.camera_uptime):
                return self.__get_up_time_content(o.camera_uptime)
        raise Exception("[Exception] Did not find former camera obj of same project id when sd file exception.")

    def get_result(self, project_id, timeout=300):
        """Get the dictionary consist of camera_uptime,camera_cpuloading_idle and camera_cpuloading_average"""
        data_dict = {}

        try:
            tn = TelnetModule(self.ip, self.account, self.password, timeout).login().send_command(
                'uptime').send_command('top -n 1')
            data = tn.result()
            camera_uptime = self.__process_camera_uptime(data[0])
            camera_cpuloading_idle, camera_load_average = self.__process_camera_cpuloading(data[1])

            try:
                before_uptime = self.find_last_valid_uptime(project_id)
                after_uptime = self.__get_up_time_content(camera_uptime)
                if not self.__up_time_is_grater_than_before(before_uptime, after_uptime):
                    camera_uptime = "[red]{0}".format(camera_uptime)
            except Exception as e:
                ptl.logging_warning('[Exception] Decide up time grater than before error. , [Error msg]:{0}'.format(e))

        except socket.timeout as e:
            ptl.logging_error('[Exception] get uptime result timeout, [Error msg]:{0}'.format(e))
            print(e)
            camera_uptime = "[red]Timeout"
            camera_cpuloading_idle = "[red]Timeout"
            camera_load_average = "[red]Timeout"

        except Exception as e:
            ptl.logging_error('[Exception] get uptime result fail, [Error msg]:{0}'.format(e))
            print(e)
            camera_uptime = "[red][Fail]"
            camera_cpuloading_idle = "[red][Fail]"
            camera_load_average = "[red][Fail]"



        data_dict["uptime"] = camera_uptime
        data_dict["idle"] = camera_cpuloading_idle
        data_dict["loadAverage"] = camera_load_average

        print(json.dumps(data_dict, ensure_ascii=False))
        return data_dict


    def __process_camera_uptime(self,data):
        """Pocess camera_uptime
        14:21:09 up 1 day,  4:24,  1 users,  load average: 5.48, 5.62, 5.65
        => 1 day,  4:24
        Keyword arguments:
        data -- The string of data that is camera uptime information

        """
        camera_uptime = re.search(b"up(.*),\s+loa",data)
        camera_uptime = camera_uptime.groups()[0]
        camera_uptime = camera_uptime.split(b',')
        if len(camera_uptime) > 2:
            camera_uptime.pop()
        camera_uptime = b' '.join(camera_uptime)
        return camera_uptime.decode()

    def __process_camera_cpuloading(self,data):
        """Pocess camera_cpuloading
        Keyword arguments:
        data -- The string of data that is camera cpuloading information
        """
        camera_cpuloading_idle = re.search(b"nice?\s(.*)\sidle",data)
        camera_cpuloading_idle = camera_cpuloading_idle.groups()[0].decode()
        camera_load_average = re.search(b"Load average:\s(\d*.\d*)\s",data)
        camera_load_average = camera_load_average.groups()[0].decode()
        return camera_cpuloading_idle, camera_load_average

    def __get_up_time_content(self, text):
        day_pattern = "\s*(\d+)\s+days\s+(\d+):(\d+)"
        min_pattern = "\s*(\d+)\s+min\s+\d\s+users"
        hour_pattren = "\s*(\d+):(\d+)\s+\d\s+users"

        if re.search(day_pattern, text):
            day = re.search(day_pattern, text).group(1)
            hour = re.search(day_pattern, text).group(2)
            min = re.search(day_pattern, text).group(3)
        elif re.search(hour_pattren, text):
            day = 0
            hour = re.search(hour_pattren, text).group(1)
            min = re.search(hour_pattren, text).group(2)
        elif re.search(min_pattern, text):
            day = 0
            hour = 0
            min = re.search(min_pattern, text).group(1)
        else:
            raise Exception("[Exception] Up time format error!")

        return int(day), int(hour), int(min)

    def __up_time_is_grater_than_before(self, before, after):
        b_day, b_hour, b_min = before
        a_day, a_hour, a_min = after

        b_total_sec = b_day * 86400 + b_hour * 3600 + b_min * 60
        a_total_sec = a_day * 86400 + a_hour * 3600 + a_min * 60
        if a_total_sec > b_total_sec:
            return True
        else:
            return False


# if __name__ == "__main__":
#     import sys
#     camera_ip = sys.argv[1]
#     camera_name = sys.argv[2]
#     camera_password = sys.argv[3]
#     # camera_ip = '172.19.16.126'
#     # camera_name = 'root'
#     # camera_password = '1'
#
#     myNasStorage = Uptime(camera_ip,camera_name,camera_password)
#     myNasStorage.get_result()