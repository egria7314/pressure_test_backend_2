#coding:utf-8
__author__ = 'steven.hsiao'
# import json
import re
from datetime import datetime as dt
from libs.pressure_test_logging import PressureTestLogging as ptl
from config.models import ProjectSetting
from camera_log.libs.cgi import CGI
from camera_log.telnet_module import URI
import time
# from telnet_module import TelnetModule
# import datetime
# import time

# VAST 1_2017-06-14_110030.3gp    2_2017-06-14_110251.3gp
# NAS "20170608/09/" + PREFIX +  "05.mp4",
class NasVastCycle():
    def __init__(self, former_file_list, new_file_list,project_id, new_file_info_dict=None ):
        self.former_file_list = former_file_list
        self.new_file_list = new_file_list
        self.new_file_info_dict = new_file_info_dict
        self.project_id = project_id

    def get_result(self, PREFIX=""):
        result = ""

        try:
            # surpass time
            # compare newest added unlocked file with former latest unlocked file & loop every added unlocked file
            try:
                task_camera_obj = ProjectSetting.objects.get(id=self.project_id)
                test_type = (task_camera_obj.type).lower()
                ptl.logging_error('[Debug] check surpass_one_hour project type:{0}'.format(test_type))
                if test_type == "high":
                    exist_surpass, comment = self.__surpass_exist()
                    if exist_surpass:
                        result += comment + '\n'
                        return result

            except Exception as e:
                ptl.logging_error('[Exception] __surpass_one_hour get result error, [Error msg]:{0}'.format(e))
                comment = e
                return comment


            # check cycle
            cycle, comment = self.__check_cycle(PREFIX)
            if cycle:
                return comment

            # loss file
            if not set(self.former_file_list).issubset(self.new_file_list) and not cycle:
                loss_locked_file_list = list(set(self.former_file_list) - set(self.new_file_list))
                result += "[red][Error] Lose file:" + ',\n'.join(loss_locked_file_list) + '\n'
                return result

            # check adding
            adding, comment = self.__check_adding(PREFIX)
            if adding:
                return comment

            else:
                result = "[red]No file created"
                return result

        except Exception as e:
            # other unknown case
            ptl.logging_error('[Exception] get storage cycle error, [Error msg]:{0}'.format(e))
            result = "[red][Fail]:{0}".format(e)
            return result


    def __check_adding(self, PREFIX=""):
        adding = False
        comment = ""

        added_file_list = list(set(self.new_file_list) - set(self.former_file_list))
        added_file_list = sorted(added_file_list)
        added_unlocked_num = len(added_file_list)

        loss_file_list = list(set(self.former_file_list) - set(self.new_file_list))
        loss_file_list = sorted(loss_file_list)
        loss_unlocked_num = len(loss_file_list)

        print(loss_unlocked_num)

        if loss_unlocked_num == 0 and added_unlocked_num > 0:
            adding = True
            comment += 'Adding'

        return adding, comment


    def __check_cycle(self, PREFIX=""):
        cycle_status = False
        comment = ""

        loss_file_list = list(set(self.former_file_list) - set(self.new_file_list))
        loss_file_list = sorted(loss_file_list)
        loss_unlocked_num = len(loss_file_list)

        added_file_list = list(set(self.new_file_list) - set(self.former_file_list))
        added_file_list = sorted(added_file_list)
        added_unlocked_num = len(added_file_list)

        # indexes of loss file
        loss_unlocked_indexes_list = [sorted(self.former_file_list).index(loss_file) for loss_file in loss_file_list ]

        # if there is old file is deleted & new file is added
        if loss_unlocked_num > 0 and added_unlocked_num > 0:
            for index_num in range(0, loss_unlocked_num):
                if not index_num in loss_unlocked_indexes_list:
                    break
                else:
                    if index_num == (loss_unlocked_num - 1):
                        cycle_status = True
                        comment += "Cycling!"

        return cycle_status, comment


    def __surpass_exist(self,):
        exist = False
        result = ""

        # if former list is empty, no need to check surpassing one hour (remember to update sd cycle)
        if self.former_file_list == []:
            return exist, result


        # first: compare newest added file with former test last file
        added_file_list = list(set(self.new_file_list) - set(self.former_file_list))
        former_last_file = sorted(set(self.former_file_list))[-1]
        added_file_list.append(former_last_file)
        added_file_list = sorted(added_file_list)

        if len(added_file_list) > 0:

            # newest_added_date = min(added_file_list)
            # if former list is empty then only compare new list

            for added_file in added_file_list:
                surpass_hour, comment = self.__surpass_one_hour(added_file)
                if surpass_hour:
                    result += comment + "\n"
                    exist = True
                    print (result)

        return exist, result

        # by MB unit
    def __get_cgi_nas_max_recording_file_size(self, camera_ip, camera_user, camera_password):
            print ("__get_cgi_nas_max_recording_file_size")
            nas_recording_index = self.__get_NAS_recording_index(camera_ip, camera_user, camera_password)
            print ("__get_NAS_recording_index_result")
            print (nas_recording_index)

            cgi_max_filesize = 'recording_i' + str(nas_recording_index) + '_maxsize'

            cgi_nas_max_file_size = CGI().get_cgi(username=camera_user, password=camera_password, host=camera_ip,
                                                 cgi_command=cgi_max_filesize, cgi_type='getparam.cgi')
            print(cgi_nas_max_file_size)
            cgi_nas_max_file_size_list = re.findall(r'\d+', cgi_nas_max_file_size.split('=')[1])
            cgi_nas_max_file_size_int = int(cgi_nas_max_file_size_list[0])

            return cgi_nas_max_file_size_int

    def __get_NAS_recording_index(self, camera_ip, camera_user, camera_password):
        """Get nas location from camera by cgi"""
        event_index = self.__get_nas_event_index(camera_ip, camera_user, camera_password)

        type_code = None
        for index in range(2):
            command = 'http://' + camera_ip + '/cgi-bin/admin/getparam.cgi?recording_i{0}_dest'.format(index)
            try:
                url = URI.set(command, camera_user, camera_password)
                url = url.read().decode('utf-8').split("\r\n")
                result = url[0].replace('recording_i{0}_dest'.format(index), '').replace("'", "").replace("=", "")
                if result != str(event_index):
                    continue
                else:
                    type_code = index
                    break
            except:
                type_code = 'get nas recording index error'

        return type_code

    def __get_nas_event_index(self, camera_ip, camera_user, camera_password):
        print ("__get_nas_event_index")
        event_index = None
        for index in range(3):
            command = 'http://' + camera_ip + '/cgi-bin/admin/getparam.cgi?server_i{0}_type'.format(index)
            try:
                url = URI.set(command, camera_user, camera_password)
                url = url.read().decode('utf-8').split("\r\n")
                result = url[0].replace('server_i{0}_type'.format(index), '').replace("'", "").replace("=", "")
                if result != 'ns':
                    continue
                else:
                    event_index = index
                    break
            except:
                event_index = 'get nas event index error'

        return event_index

    # compare two date if surpass one hour
    def __surpass_one_hour(self, added_file):
        log = ""
        task_camera_obj = ProjectSetting.objects.get(id=self.project_id)
        camera_ip = task_camera_obj.ip
        camera_user = task_camera_obj.username
        camera_password = task_camera_obj.password
        max_size = self.__get_cgi_nas_max_recording_file_size(camera_ip, camera_user, camera_password)


        file_duration = self.new_file_info_dict[added_file]["Duration"]
        file_size = self.new_file_info_dict[added_file]["Size"]
        if file_duration: # Continue recording video has no duration.
            # if differ is more than or less one hour , difference value +-1
            seconds_of_one_hour = 3600
            # seconds_of_one_hour = 60 # for quickly test camera log
            if file_duration > seconds_of_one_hour + 1:
                log = "[red][Error] {0}'s file is surpass one hour!!".format(added_file)
                return True, log

            elif file_duration < seconds_of_one_hour - 1:
                # ex: if cgi is 2000M, then 1999~2001M pass
                if (file_size <= max_size + 1 and file_size >= max_size - 1):
                    return False, log
                else:
                    log = "[red][Error] {0}'s file is less than one hour!!".format(added_file)
                    return True, log


        return False, log


def trans_vast_file_to_nas_style(vast_sty_file_list):
    nas_sty_file_list = []

    # 1_2017-06-14_110030.3gp    >   20170614/11/00.3gp
    for file in vast_sty_file_list:
        # m = re.match(r"(\w+) (\w+)", "Isaac Newton, physicist")
        m = re.match(r"(\d+)_(\d+)-(\d+)-(\d+)_(\d{2})(\d{2})(\d{2})\.", file)
        # print(m.group(0))
        year = m.group(2)
        mon = m.group(3)
        day = m.group(4)
        hour = m.group(5)
        min = m.group(6)

        nas_sty_vastfile_str = year + mon + day + '/' + hour + '/' + min + '.3gp'

        nas_sty_file_list.append(nas_sty_vastfile_str)


    return nas_sty_file_list

#
# if __name__ == "__main__":
#     # while(True):
#     #     return_recording_status()
#     #     time.sleep(5)
#     PREFIX = "TEST"
#
#     # NAS file
#     # loss case
#     # former_file_list = ["20170608/09/" + PREFIX + "07.mp4", "20170608/09/" + PREFIX + "08.mp4"]
#     # former_file_list = []
#     # new_file_list = ["20170608/09/" + PREFIX + "07.mp4", "20170608/09/" + PREFIX + "10.mp4", "20170608/09/" + PREFIX + "11.mp4"]
#
#     # surpass one hour
#     # former_file_list = ["20170608/09/" + PREFIX + "07.mp4", "20170608/09/" + PREFIX + "08.mp4"]
#     # new_file_list =    ["20170608/09/" + PREFIX + "07.mp4", "20170608/09/" + PREFIX + "08.mp4",
#     #                     "20170608/10/" + PREFIX + "11.mp4", "20170609/10/" + PREFIX + "12.mp4", "20170609/11/" + PREFIX + "13.mp4",]
#
#     # cycle
#     # former_file_list = ["20170608/09/" + PREFIX + "07.mp4", "20170608/09/" + PREFIX + "08.mp4", "20170608/09/" + PREFIX + "09.mp4"]
#     # former_file_list = []
#     # new_file_list =    ["20170608/09/" + PREFIX + "09.mp4", "20170608/09/" + PREFIX + "10.mp4"]
#
#     # Adding
#     # former_file_list = ["20170608/09/" + PREFIX + "07.mp4", "20170608/09/" + PREFIX + "08.mp4"]
#     # former_file_list = []
#     # new_file_list =    ["20170608/09/" + PREFIX + "07.mp4", "20170608/09/" + PREFIX + "08.mp4", "20170608/09/" + PREFIX + "09.mp4"]
#
#     ##################################################################################################################################
#     # VAST file
#     #
#     # # loss case
#     # vast_former_list = ["1_2017-06-14_110030.3gp", "1_2017-06-14_140030.3gp"]
#     # vast_new_list = ["1_2017-06-14_110030.3gp"]
#     #
#     # # surpass one hour
#     # vast_former_list = ["1_2017-06-14_110030.3gp", "1_2017-06-14_140030.3gp"]
#     # vast_new_list = ["1_2017-06-14_154030.3gp", "1_2017-06-14_180030.3gp"]
#
#     # # cycle
#     # vast_former_list = ["1_2017-06-14_110030.3gp", "1_2017-06-14_140030.3gp"]
#     # vast_new_list = [ "1_2017-06-14_140030.3gp", "1_2017-06-14_142030.3gp",]
#
#     # Adding:
#     # vast_former_list = ["1_2017-06-14_110030.3gp", "1_2017-06-14_140030.3gp"]
#     # vast_new_list = ["1_2017-06-14_110030.3gp", "1_2017-06-14_140030.3gp", "1_2017-06-14_144030.3gp" ]
#
#
#
#     former_file_list = trans_vast_file_to_nas_style(vast_former_list)
#     new_file_list = trans_vast_file_to_nas_style(vast_new_list)
#
#     print(former_file_list)
#     print(new_file_list)
#     cycle_obj = NasVastCycle(former_file_list, new_file_list)
#     print('++result++')
#
#     # NAS:
#     print(cycle_obj.get_result(cycle_obj.former_file_list, cycle_obj.new_file_list, PREFIX))
#
#     # VAST
#     # print(cycle_obj.get_result(cycle_obj.former_file_list, cycle_obj.new_file_list))
#     print('++')