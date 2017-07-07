__author__ = 'carlos.hu'
from camera_log.telnet_module import TelnetModule
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

    def get_result(self, timeout=300):
        """Get the dictionary consist of camera_uptime,camera_cpuloading_idle and camera_cpuloading_average"""
        data_dict = {}

        try:
            tn = TelnetModule(self.ip,self.account,self.password, timeout).login().send_command('uptime').send_command('top -n 1')
            data = tn.result()
            camera_uptime = self.__process_camera_uptime(data[0])
            camera_cpuloading_idle, camera_load_average = self.__process_camera_cpuloading(data[1])

        except socket.timeout as e:
            ptl.logging_error('[Exception] get uptime result timeout, [Error msg]:{0}'.format(e))
            print(e)
            camera_uptime = "Timeout"
            camera_cpuloading_idle = "Timeout"
            camera_load_average = "Timeout"

        except Exception as e:
            ptl.logging_error('[Exception] get uptime result fail, [Error msg]:{0}'.format(e))
            print(e)
            camera_uptime = "[Fail]"
            camera_cpuloading_idle = "[Fail]"
            camera_load_average = "[Fail]"


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