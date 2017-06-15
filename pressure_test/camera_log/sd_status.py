__author__ = 'steven.hsiao'
import json
import re

# from pressure_test.camera_log.telnet_module import URI
from camera_log.telnet_module import URI

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

    def get_result(self):
        """Get the dictionary consist of camera SD status and usedpercent"""
        data_dict = {}
        SD_status = self.__get_sd_status()
        data_dict["sdCardStatus"] = SD_status[0]
        data_dict["sdCardUsed"] = self.__get_sd_status()[1]
        #data_dict["SD_recording_filename"] = self.__get_recording_filename()
        print(json.dumps(data_dict, ensure_ascii=False))
        return data_dict

    def __get_sd_status(self):
        """Get SD status from camera by cgi"""
        command = 'http://'+self.ip+'/cgi-bin/admin/lsctrl.cgi?cmd=queryStatus&retType=javascript'
        url = URI.set(command, self.account, self.password)
        data = url.read().decode()
        print(data)


        sd_status = re.search("cond='(.*)'",data).groups()[0]
        sd_status_totalsize = re.search("totalsize='(.*)'",data).groups()[0]
        sd_status_usedspace = re.search("usedspace='(.*)'",data).groups()[0]
        sd_used_percent = (float(sd_status_usedspace)/float(sd_status_totalsize))*100

        return sd_status,(round(sd_used_percent, 2))


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
