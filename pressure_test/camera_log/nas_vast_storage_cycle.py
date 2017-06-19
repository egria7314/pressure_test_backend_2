#coding:utf-8
__author__ = 'steven.hsiao'
# import json
import re
from datetime import datetime as dt
import time
# from telnet_module import TelnetModule
# from telnet_module import URI
# import datetime
# import time

# VAST 1_2017-06-14_110030.3gp    2_2017-06-14_110251.3gp
# NAS "20170608/09/" + PREFIX +  "05.mp4",
class NasVastCycle():
    def __init__(self, former_file_list, new_file_list):
        self.former_file_list = former_file_list
        self.new_file_list = new_file_list

    def get_result(self, PREFIX=""):
        result = ""


        try:
            # surpass time
            # compare newest added unlocked file with former latest unlocked file & loop every added unlocked file
            exist_surpass, comment = self.__surpass_exist(PREFIX)
            if exist_surpass:
                result += comment + '\n'
                return result

            # check cycle
            cycle, comment = self.__check_cycle(PREFIX)
            if cycle:
                return comment

            # loss file
            if not set(self.former_file_list).issubset(self.new_file_list) and not cycle:
                loss_locked_file_list = list(set(self.former_file_list) - set(self.new_file_list))
                result += "Error! Lose file:" + ','.join(loss_locked_file_list) + '\n'
                return result

            # check adding
            adding, comment = self.__check_adding(PREFIX)
            if adding:
                return comment

            else:
                result = "Nothing change!"
                return result

        except:
            # other unknown case
            result = "Fail"
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


    def __surpass_exist(self, PREFIX=""):
        exist = False
        result = ""

        # first: compare newest added file with former test last file
        added_file_list = list(set(self.new_file_list) - set(self.former_file_list))
        added_file_list = sorted(added_file_list)

        if len(added_file_list) > 0:
            newest_added_date = min(added_file_list)
            # if former list is empty then only compare new list
            if len(self.former_file_list) != 0:
                oldest_former_date = max(self.former_file_list)
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
    def __surpass_one_hour(self, former_date, newer_date, PREFIX=""):
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
            old_file_min = old_re[2].split(PREFIX)[1].split(".")[0]
            new_file_min = new_re[2].split(PREFIX)[1].split(".")[0]
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

def trans_vast_file_to_nas_style(vast_sty_file_list):
    nas_sty_file_list = []
    print(vast_sty_file_list)

    # 1_2017-06-14_110030.3gp    >   20170614/11/00.3gp
    for file in vast_sty_file_list:
        # m = re.match(r"(\w+) (\w+)", "Isaac Newton, physicist")
        m = re.match(r"(\d+)_(\d+)-(\d+)-(\d+)_(\d{2})(\d{2})(\d{2})\.", file)
        print("TEST!!")
        # print(m.group(0))
        year = m.group(2)
        mon = m.group(3)
        day = m.group(4)
        hour = m.group(5)
        min = m.group(6)

        nas_sty_vastfile_str = year + mon + day + '/' + hour + '/' + min + '.3gp'

        print("End")
        # print(m)

        nas_sty_file_list.append(nas_sty_vastfile_str)

    # print(nas_sty_file_list)

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