__author__ = "steven.hsiao"

from camera_log.telnet_module import TelnetModule
from libs.pressure_test_logging import PressureTestLogging as ptl
import re
import json
import socket

class Epochtime(object):
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
            tn = TelnetModule(self.ip,self.account,self.password, timeout).login().send_command('date +%s')
            data = tn.result()
            camera_epoch_time = self.__process_camera_epoch_time(data[0])
        except socket.timeout as e:
            ptl.logging_error('[Exception] get epoch time time out, [Error msg]:{0}'.format(e))
            print(e)
            camera_epoch_time = "Timeout"
        except Exception as e:
            ptl.logging_error('[Exception] get epoch time error, [Error msg]:{0}'.format(e))
            print(e)
            camera_epoch_time = "[Fail]"

        data_dict["camera_epoch_time"] = camera_epoch_time
        print(json.dumps(data_dict, ensure_ascii=False))
        return data_dict



    def __process_camera_epoch_time(self,data):
        """Pocess camera_epoch_time
        14:21:09 up 1 day,  4:24,  1 users,  load average: 5.48, 5.62, 5.65
        => 1 day,  4:24
        Keyword arguments:
        data -- The string of data that is camera uptime information

        """
        camera_epoch_time = re.search(b"(\d+)",data)
        camera_epoch_time = camera_epoch_time.groups()[0].decode()

        return camera_epoch_time


# if __name__ == "__main__":
#     import sys
#     camera_ip = sys.argv[1]
#     camera_name = sys.argv[2]
#     camera_password = sys.argv[3]
#     # camera_ip = '172.19.1.23'
#     # camera_name = 'root'
#     # camera_password = '1'
#
#     camera_epoch_time = EpochTime(camera_ip,camera_name,camera_password)
#     camera_epoch_time.get_result()