__author__ = 'steven.hsiao'
import json
import re
import socket

# from pressure_test.camera_log.telnet_module import URI
from camera_log.telnet_module import URI
from libs.pressure_test_logging import PressureTestLogging as ptl

class SDstatus(object):
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

    def change_sd_status_prefix(self, status):
        if 'ready' in status: # In this case, status will not be "not support".
            return status
        else:
            return '[red]{0}'.format(status)

    def get_result(self, timeout=300):
        """Get the dictionary consist of camera SD status and usedpercent"""
        data_dict = {}

        try:
            SD_status, SD_used = self.__get_sd_status(timeout)
            data_dict["sdCardStatus"] = self.change_sd_status_prefix(SD_status)
            data_dict["sdCardUsed"] = self.change_sd_status_prefix(SD_used)
        except socket.timeout as e:
            ptl.logging_error('[Exception] get sd status time out, [Error msg]:{0}'.format(e))
            data_dict["sdCardStatus"] = "[red]Timeout"
            data_dict["sdCardUsed"] = "[red]Timeout"

        except Exception as e:

            print("******SD issue:*****")
            print(e)
            if "detached" in str(e):
                ptl.logging_warning('[warning] sd detached, [Error msg]:{0}'.format(e))
                data_dict["sdCardStatus"] = "[red]detached"
                data_dict["sdCardUsed"] = "[red]detached"
            else:
                ptl.logging_error('[Exception] get  error, [Error msg]:{0}'.format(e))
                data_dict["sdCardStatus"] = "[red][Fail]"
                data_dict["sdCardUsed"] = "[red][Fail]"

            # if e == "disk_i0_cond=detached":
            #
            #     data_dict["sdCardStatus"] = "detached"
            #     data_dict["sdCardUsed"] = "detached"
            # else:
            #     data_dict["sdCardStatus"] = "Fail"
            #     data_dict["sdCardUsed"] = "Fail"

        #data_dict["SD_recording_filename"] = self.__get_recording_filename()
        print(json.dumps(data_dict, ensure_ascii=False))
        return data_dict

    def __get_sd_status(self, timeout=300):
        """Get SD status from camera by cgi"""
        command = 'http://'+self.ip+'/cgi-bin/admin/lsctrl.cgi?cmd=queryStatus&retType=javascript'
        url = URI.set(command, self.account, self.password, timeout)
        data = url.read().decode()
        print(data)


        sd_status = re.search("cond='(.*)'",data).groups()[0]
        sd_status_totalsize = re.search("totalsize='(.*)'",data).groups()[0]
        sd_status_usedspace = re.search("usedspace='(.*)'",data).groups()[0]
        try:
            sd_used_percent = (float(sd_status_usedspace)/float(sd_status_totalsize))*100
            sd_used_percent = str(round(sd_used_percent, 2)) + "%"
        except Exception as e:
            ptl.logging_warning('[Warning] sd used percent calculate error. [Error msg]:{0}'.format(e))
            sd_used_percent = sd_status

        return sd_status, sd_used_percent


# if __name__ == "__main__":
#     # myNasStorage = SDstatus('172.19.16.126','root','1')
#     # myNasStorage.get_result()
#     import sys
#     camera_ip = sys.argv[1]
#     camera_name = sys.argv[2]
#     camera_password = sys.argv[3]
#
#     myNasStorage = SDstatus(camera_ip,camera_name,camera_password)
#     myNasStorage.get_result()
