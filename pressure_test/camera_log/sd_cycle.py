__author__ = 'steven.hsiao'
import json
import re
from datetime import datetime as dt
from libs.pressure_test_logging import PressureTestLogging as ptl

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


    def get_result(self, PREFIX):
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
            # loss locked file
            if not set(self.former_locked_file_list).issubset(self.new_all_file):
                loss_locked_file_list = list(set(self.former_locked_file_list) - set(self.new_all_file))
                result += "Error! Lose file (locked file loss!):" + ','.join(loss_locked_file_list) + '\n'
                return result

            # surpass time
            # compare newest added unlocked file with former latest unlocked file & loop every added unlocked file
            exist_surpass, comment = self.__surpass_exist(PREFIX)
            if exist_surpass:
                result += comment + '\n'
                return result

            # loss unlocked file (unlock of 1 is not subset of 2)
            if not set(self.former_unlocked_file_list).issubset(self.new_unlocked_file_list):
                loss_unlocked_file_list = list(set(self.former_unlocked_file_list) - set(self.new_unlocked_file_list))
                result += "Error! Lose file (unlocked file loss!):" + ','.join(loss_unlocked_file_list) + '\n'
                return result

            # check cycle
            cycle, comment = self.__check_cycle(PREFIX)
            if cycle:
                return comment


            # check adding
            adding, comment = self.__check_adding(PREFIX)
            if adding:
                return comment

            else:
                result = "Nothing change!"
                return result
        except Exception as e:
            ptl.logging_error('[Exception] get sd cycle error, [Error msg]:{0}'.format(e))
            print("SD Cycle Fail:")
            print(e)
            result = "Fail"
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



    def __surpass_exist(self, PREFIX):
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
                surpass_hour, comment = self.__surpass_one_hour(oldest_former_date, newest_added_date, PREFIX)
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
                        surpass_hour, comment = self.__surpass_one_hour(added_file_list[index - 1], added_file_list[index], PREFIX)
                        if surpass_hour:
                            result += comment + "\n"
                            exist = True

        return exist, result


    # compare two date if surpass one hour
    def __surpass_one_hour(self, former_date, newer_date, PREFIX):
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

        # if differ is more than one hour
        if differ_seconds > 3600:
            log = "Error! " + new_datetime + "'s file is " + "Surpass one hour!!"
            return True, log
        else:
            return False, log

