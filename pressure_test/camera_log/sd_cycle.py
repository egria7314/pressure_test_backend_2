__author__ = 'steven.hsiao'
import json
import re
from datetime import datetime as dt
from libs.pressure_test_logging import PressureTestLogging as ptl
from config.models import ProjectSetting
from camera_log.telnet_module import TelnetModule
from camera_log.telnet_module import URI
from camera_log.libs.cgi import CGI


class SDcycle(object):
    def __init__(self, former_locked_file_list, former_unlocked_file_list, new_locked_file_list, new_unlocked_file_list):
        """
        Keyword arguments:
        ip -- the string of ip that is camera ip
        account -- the string of account that is camera account
        password -- the string of password that is camera password
        """
        self.former_locked_file_list = former_locked_file_list
        self.former_unlocked_file_list = former_unlocked_file_list
        self.former_all_file =  former_locked_file_list + former_unlocked_file_list
        self.new_locked_file_list = new_locked_file_list
        self.new_unlocked_file_list = new_unlocked_file_list
        self.new_all_file = new_locked_file_list + new_unlocked_file_list


    def get_result(self, PREFIX, project_id):
        result = ""
        # print("******set(self.former_locked_file_list)**********")
        # print(set(self.former_locked_file_list))
        # print("******self.new_all_file**********")
        # print(self.new_all_file)
        # print("******set(self.former_unlocked_file_list)**********")
        # print(set(self.former_unlocked_file_list))
        # print("******self.new_unlocked_file_list**********")
        # print(self.new_unlocked_file_list)



        try:
            # surpass time
            # compare newest added unlocked file with former latest unlocked file & loop every added unlocked file
            exist_surpass, comment = self.__surpass_exist(PREFIX, project_id)
            if exist_surpass:
                result += comment + '\n'
                return result

            # check cycle
            cycle, comment = self.__check_cycle(PREFIX)
            if cycle:
                return comment

            # loss unlocked file (unlock of 1 is not subset of 2)
            if not set(self.former_unlocked_file_list).issubset(self.new_unlocked_file_list):
                loss_unlocked_file_list = list(set(self.former_unlocked_file_list) - set(self.new_unlocked_file_list))
                result += "[red][Error] Lose file (unlocked file loss!):" + ','.join(loss_unlocked_file_list) + '\n'
                return result

            # loss locked file
            if not set(self.former_locked_file_list).issubset(self.new_all_file):
                loss_locked_file_list = list(set(self.former_locked_file_list) - set(self.new_all_file))
                result += "[red][Error] Lose file (locked file loss!):" + ','.join(loss_locked_file_list) + '\n'
                return result

            # check adding
            adding, comment = self.__check_adding(PREFIX)
            if adding:
                return comment
            else:
                result = "[red]No file created"
                return result
        except Exception as e:
            ptl.logging_error('[Exception] get sd cycle error, [Error msg]:{0}'.format(e))
            print("SD Cycle Fail:")
            print(e)
            result = "[red][Fail]"
            return result


    def __check_adding(self, PREFIX):
        adding = False
        comment = ""

        added_file_list = list(set(self.new_unlocked_file_list) - set(self.former_unlocked_file_list))
        added_file_list = sorted(added_file_list)
        added_unlocked_num = len(added_file_list)
        # print('TEST Added')
        # print(added_file_list)

        loss_file_list = list(set(self.former_unlocked_file_list) - set(self.new_unlocked_file_list))
        loss_file_list = sorted(loss_file_list)
        loss_unlocked_num = len(loss_file_list)

        # print(loss_unlocked_num)

        if loss_unlocked_num == 0 and added_unlocked_num > 0:
            adding = True
            comment += 'Adding'

        return adding, comment


    def __check_cycle(self, PREFIX):
        cycle_status = False
        comment = ""

        loss_file_list = list(set(self.former_unlocked_file_list) - set(self.new_unlocked_file_list))
        loss_file_list = sorted(loss_file_list)
        loss_unlocked_num = len(loss_file_list)

        added_file_list = list(set(self.new_unlocked_file_list) - set(self.former_unlocked_file_list))
        added_file_list = sorted(added_file_list)
        added_unlocked_num = len(added_file_list)

        # indexes of loss file
        loss_unlocked_indexes_list = [sorted(self.former_unlocked_file_list).index(loss_file) for loss_file in loss_file_list ]

        # indexes of added file
        # added_unlocked_indexes_list = [self.new_unlocked_file_list.index(added_file) for added_file in added_file_list]

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



    def __surpass_exist(self, PREFIX, project_id):
        exist = False
        result = ""

        if self.former_unlocked_file_list == [] and self.former_locked_file_list == []:
            return exist, result


        # first: compare newest added file with former test last file
        added_file_list = list(set(self.new_unlocked_file_list) - set(self.former_unlocked_file_list))
        added_file_list = sorted(added_file_list)

        # print("Unlocked Added:")
        # print(added_file_list)

        if len(added_file_list) != 0:
            newest_added_date = min(added_file_list)
            former_unlocked = self.former_unlocked_file_list
            # if former list is empty then only compare new list
            if len(former_unlocked) > 0:
                oldest_former_date = max(former_unlocked)
                surpass_hour, comment = self.__surpass_one_hour(oldest_former_date, newest_added_date, PREFIX, project_id)
                if surpass_hour:
                    result = comment + '\n'
                    exist = True

            # second: check if every added file is surpass one hour
            for added_file in added_file_list:
                if added_file == newest_added_date:
                    pass
                # loop every added file except first file
                else:
                    index = added_file_list.index(added_file)
                    if index >= 1:
                        surpass_hour, comment = self.__surpass_one_hour(added_file_list[index - 1], added_file_list[index], PREFIX, project_id)
                        if surpass_hour:
                            result += comment + "\n"
                            exist = True

        return exist, result


    # compare two date if surpass one hour
    def __surpass_one_hour(self, former_date, newer_date, PREFIX, project_id):
        ptl.logging_warning('[TEST!!!] former_date, [TEST!!! msg]:{0}'.format(former_date))
        ptl.logging_warning('[TEST!!!] newer_date, [TEST!!! msg]:{0}'.format(newer_date))

        log = ""
        # print("oldest former:" + former_date)
        # print("newest added:" + newer_date)
        result = False

        # old
        old_re = re.split("/", former_date)  # ['20170608', '09', 'TEST10.mp4']
        new_re = re.split("/", newer_date)
        # print(old_re)
        old_year = old_re[0][:4]
        old_mon = old_re[0][4:6]
        old_day = old_re[0][6:]
        old_folder_hour = old_re[1]

        if PREFIX != "":
            old_file_min = old_re[2].split(PREFIX)[1].split(".")[0][:2]
            new_file_min = new_re[2].split(PREFIX)[1].split(".")[0][:2]
        else:
            old_file_min = old_re[2].split(".")[0]
            new_file_min = new_re[2].split(".")[0]

        old_datetime = old_year + '/' + old_mon + '/' + old_day + ' ' + old_folder_hour + ':' + old_file_min
        old_date_obj = dt.strptime(old_datetime, "%Y/%m/%d %H:%M")

        new_year = new_re[0][:4]
        new_mon = new_re[0][4:6]
        new_day = new_re[0][6:]
        new_folder_hour = new_re[1]

        # new_file_min = new_re[2].split(PREFIX)[1].split(".")[0]  # new_re[2] is like: 'TEST10.mp4'
        new_datetime = new_year + '/' + new_mon + '/' + new_day + ' ' + new_folder_hour + ':' + new_file_min
        new_date_obj = dt.strptime(new_datetime, "%Y/%m/%d %H:%M")

        differ_seconds = (new_date_obj - old_date_obj).total_seconds()

        # if differ is more than or less one hour , difference value +-1
        seconds_of_one_hour = 3600
        if differ_seconds > seconds_of_one_hour + 1:
            log = "[red][Error] " + new_datetime + "'s file is " + "Surpass one hour!!"
            return True, log
        elif differ_seconds < seconds_of_one_hour - 1:
            try:
                task_camera_obj = ProjectSetting.objects.get(id=project_id)
                camera_ip = task_camera_obj.ip
                camera_user = task_camera_obj.username
                camera_password = task_camera_obj.password

                sd_file_size_mb = self.__check_sd_filesize(project_id, newer_date, camera_ip, camera_user, camera_password)
                cgi_sd_max_file_size_mb = self.__get_cgi_sd_max_recording_file_size(camera_ip, camera_user, camera_password)

                # ex: iif cgi is 2000M, then 1999~2001M pass
                if (sd_file_size_mb <= cgi_sd_max_file_size_mb + 1 and sd_file_size_mb >= cgi_sd_max_file_size_mb - 1):
                    return False, log
                else:
                    log = "[red][Error] " + new_datetime + "'s file is " + "less than one hour!!"
                    return True, log

            except Exception as e:
                ptl.logging_error('[ERROR] check less than one hour error, [Error msg]:{0}'.format(e))
                return False, log

        else:
            return False, log


    def __check_sd_filesize(self, project_id, file_info, camera_ip, camera_user, camera_password):
        illegal_bool = True

        # task_camera_obj = ProjectSetting.objects.get(id=project_id)
        # camera_ip = task_camera_obj.ip
        # camera_user = task_camera_obj.username
        # camera_password = task_camera_obj.password

        get_file_size_dir = '/mnt/auto/CF/NCMF/' + file_info    #20170830/16/medium_stress36.mp4'
        tn = TelnetModule(camera_ip, camera_user, camera_password).login().send_command('du ' + get_file_size_dir)

        result = tn.result()[0]
        split_list = result.split(get_file_size_dir.encode())
        split_list = [element.decode() for element in split_list]
        print(split_list)
        kb_size_list = re.findall(r'\d+', split_list[1])
        mb_size_int = int(kb_size_list[0]) / 1024    # KB to MB
        ptl.logging_warning('[Warning] check file MB size when check less than one hour:, [Error msg]:{0}'.format(mb_size_int))
        mb_size = mb_size_int

        return mb_size


    # by MB unit
    def __get_cgi_sd_max_recording_file_size(self, camera_ip, camera_user, camera_password):
        sd_recording_index = self.__get_sd_recording_index(camera_ip, camera_user, camera_password)

        cgi_max_filesize = 'recording_i' + str(sd_recording_index) + '_maxsize'

        cgi_sd_max_file_size = CGI().get_cgi(username=camera_user, password=camera_password, host=camera_ip, cgi_command=cgi_max_filesize, cgi_type='getparam.cgi')
        print(cgi_sd_max_file_size)
        cgi_sd_max_file_size_list = re.findall(r'\d+', cgi_sd_max_file_size.split('=')[1])
        cgi_sd_max_file_size_int = int(cgi_sd_max_file_size_list[0])

        return cgi_sd_max_file_size_int



    def __get_sd_recording_index(self, camera_ip, camera_user, camera_password):
        """Get nas location from camera by cgi"""
        type_code = None
        for index in range(2):
            command = 'http://'+camera_ip+'/cgi-bin/admin/getparam.cgi?recording_i{0}_dest'.format(index)
            try:
                url = URI.set(command, camera_user, camera_password)
                url = url.read().decode('utf-8').split("\r\n")
                result = url[0].replace('recording_i{0}_dest'.format(index), '').replace("'", "").replace("=", "")
                if result != 'cf':
                    continue
                else:
                    type_code = index
                    break
            except:
                type_code = 'get sd recording index error'

        return type_code

