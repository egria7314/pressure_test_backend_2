# __author__ = 'steven.hsiao'
# # -*- coding: utf-8 -*-
import json
import re
from camera_log.telnet_module import TelnetModule
from camera_log.telnet_module import URI

import datetime
import time
#
# class Sdrecordingfile(object):
#     def __init__(self, ip, account, password):
#         """
#         Keyword arguments:
#         ip -- the string of ip that is camera ip
#         account -- the string of account that is camera account
#         password -- the string of password that is camera password
#         """
#         self.ip = ip
#         self.account = account
#         self.password = password
#
#     def get_ftp_all_filename(self):
#         """Get all recording file from SD card."""
#         print("**TEST1**")
#         tn = TelnetModule(self.ip, self.account, self.password).login().send_command('find /mnt/auto/CF/NCMF -name "*.mp4"')
#         print("**TEST2**")
#         filename =  re.findall(b"NCMF\D(.*)",tn.result()[0])
#         print("**TEST3**")
#         for i in range(len(filename)):
#             filename[i] = filename[i].strip().decode()
#         filename.remove("-name \"*.mp4\"")
#         return filename
#
#     def get_ui_all_filename(self):
#         """Get all recording file from UI by cgi."""
#         command = 'http://'+self.ip+'/cgi-bin/admin/lsctrl.cgi?cmd=search'
#         url = URI.set(command, self.account, self.password)
#         data = url.read()
#         filename = re.findall(b"NCMF\D\D(.*)<",data)
#         file_starttime =  re.findall(b"beginTime>(.*)<",data)
#         file_endtime   =  re.findall(b"endTime>(.*)<",data)
#         all_file=[]
#
#         #all_file : [filename,starttime,file_endtime]
#         for i in range(len(filename)):
#             all_file.append([filename[i], file_starttime[i], file_endtime[i]])
#
#         for i in range(len(all_file)):
#             # for j in range(len(all_file[i])):
#             all_file[i] = [x.decode() for x in all_file[i]]
#
#         print("----------TEST100----------")
#         # print(all_file)
#         # # print(test)
#         # print("----------------------")
#
#
#         #TO DO:for datetime format
#         #'2016-04-01 00:44:56.637'
#         #['2016', '04', '01', '00', '44', '56', '637']
#         # test = []
#         for i in range(len(all_file)):
#             for j in range(1,len(all_file[0]),1):
#                 all_file[i][j] = re.split('-| |:|\.',all_file[i][j])
#
#                 # all_file[i][j] = [x.decode() for x in all_file[i][j]]
#                 # print(all_file[i][j])
#
#         # for e in all_file:
#
#         print("--------**----------")
#         print(all_file)
#         # # print(test)
#         print("----------------------")
#
#
#         return all_file
#
#     def continuous_filename_time(self):
#         """Get locked continuous_filename begin time and end time."""
#         restart_status = 0
#         locked_file = self.__get_continuous_locked_filename_time()
#         for file in locked_file:
#             #index = 2 ,that is file endtime
#             #if file[2] is None,stop recording
#             if not file[2]:
#                 restart_status = 1
#                 self.__restart_recording()
#
#         if restart_status == 0:
#             return self.__process_continuous_filename(locked_file)
#         else :
#             return 'restart'
#
#     def __get_continuous_locked_filename_time(self):
#         """Get locked continuous_filename begin time and end time."""
#         command = 'http://'+self.ip+'/cgi-bin/admin/lsctrlrec.cgi?cmd=getSlices'
#         url = URI.set(command, self.account, self.password)
#         data = url.read()
#         islocked = re.findall(b"<islocked>(\d)",data)
#         lockedfile_starttime = re.findall(b"sliceStart>(.*)<",data)
#         lockedfile_endtime   = re.findall(b"sliceEnd>(.*)<",data)
#         lockedfile = []
#
#         #remove unlocked file info (isLocked = 0)
#         #lockedfile = [islocked,starttime,endtime] = ['1', '2016-03-31T16:44:56.637Z', '2016-03-31T16:46:23.583Z']
#         for i in range(len(islocked)):
#             if  islocked[i] !='0' :
#                 lockedfile.append([islocked[i], lockedfile_starttime[i], lockedfile_endtime[i]])
#         return lockedfile
#
#     def __restart_recording(self):
#         """Restart camera by cgi"""
#         command = 'http://'+self.ip+'/cgi-bin/admin/setparam.cgi?recording_i0_enable=0'
#         URI.set(command, self.account, self.password)
#         time.sleep(3)
#         command = 'http://'+self.ip+'/cgi-bin/admin/setparam.cgi?recording_i0_enable=1'
#         URI.set(command, self.account, self.password)
#         #avoid to blank info
#         time.sleep(10)
#
#     def __process_continuous_filename(self,data):
#         """Process continuous filename contrast to datetime"""
#         file_time = data
#         #['1', '2016-03-31T16:44:56.637Z', '2016-03-31T16:46:23.583Z']
#         #['1', ['2016', '03', '31', '16', '44', '56', '637'], ['2016', '03', '31', '16', '46', '23', '583']]
#         for file in range(len(file_time)):
#             for time in range(1,len(file_time[0]),1):
#                 file_time[file][time] = re.split(b'-|T|:|\.|Z',file_time[file][time])
#                 #remove blank element
#                 # file_time[file][time] = filter(None, file_time[file][time])              # python 2 style
#                 file_time[file][time] =  [_f for _f in file_time[file][time] if _f]        # python 3 style
#
#
#         return file_time
#
#     def get_fw_file_dict(self):
#         # ori
#         # try:
#         #     command = 'http://'+self.ip+'/cgi-bin/admin/lsctrlrec.cgi?cmd=getSlices'
#         #     URI.set(command, self.account, self.password)
#         #     return self.get_new_fw_file_dict()
#         # except:
#         #     return self.get_old_fw_file_dict()
#
#         command = 'http://'+self.ip+'/cgi-bin/admin/lsctrlrec.cgi?cmd=getSlices'
#         URI.set(command, self.account, self.password)
#         return self.get_new_fw_file_dict()
#
#
#
#
#     def get_old_fw_file_dict(self):
#         print("*****OLD!!!!*****")
#         file_dict={}
#         unlocked_file =[]
#         ftp_all_filename = self.get_ftp_all_filename()
#
#         command = 'http://'+self.ip+'/cgi-bin/admin/lsctrl.cgi?cmd=search&isLocked=1'
#         url = URI.set(command, self.account, self.password)
#         data = url.read()
#         locked_file = re.findall(b"NCMF\D\D(.*)<",data)
#
#         print('**TEST4X**')
#         #remove event recording
#         for file_name in ftp_all_filename:
#             if 'event'in file_name:
#                 ftp_all_filename.remove(file_name)
#
#         #compare ftp_all_filename,remove FW fake recording (FW-Bug)
#         for file_name in locked_file:
#             if file_name not in ftp_all_filename:
#                 locked_file.remove(file_name)
#
#         for file_name in ftp_all_filename:
#             if file_name not in locked_file:
#                 unlocked_file.append(file_name)
#
#
#         file_dict["all_file"] = ftp_all_filename
#         file_dict["locked_file"] = locked_file
#         file_dict["unlocked_file"] = unlocked_file
#
#         print('***TEST6****')
#         # print(file_dict)
#         print('***TEST7****')
#
#
#
#         print(json.dumps(file_dict, ensure_ascii=False))
#         return file_dict
#
#     def get_new_fw_file_dict(self):
#         """Return recording files by categories in dictionary
#
#         Key1 : all_file ;
#         Key2 : locked_file;
#         Key3 : unlocked_file;
#         """
#         print("*****NEW!!!*****")
#         file_dict={}
#         print('***TEST30****')
#         ftp_all_filename = self.get_ftp_all_filename()
#         print('***TEST31****')
#         ui_all_filename =self.get_ui_all_filename()
#         print('***TEST32****')
#         while 1:
#             print('***TEST33****')
#             continuous_filename_time = self.continuous_filename_time()
#             print('***TEST34****')
#             if continuous_filename_time != 'restart':
#                 print('***TEST35****')
#                 break
#         print('***TEST36****')
#         locked_file = self.__get_locked_filename(ui_all_filename, continuous_filename_time)
#
#         print(locked_file)
#
#         print('***TEST37**!**')
#         unlocked_file =[]
#
#         #remove event recording
#         for file_name in ftp_all_filename:
#             if 'event'in file_name:
#                 ftp_all_filename.remove(file_name)
#
#         #compare ftp_all_filename,remove FW fake recording (FW-Bug)
#         for file_name in locked_file:
#             if file_name not in ftp_all_filename:
#                 locked_file.remove(file_name)
#
#         for file_name in ftp_all_filename:
#             if file_name not in locked_file:
#                 unlocked_file.append(file_name)
#
#
#         file_dict["all_file"] = ftp_all_filename
#         file_dict["locked_file"] = locked_file
#         file_dict["unlocked_file"] = unlocked_file
#
#         print(json.dumps(file_dict, ensure_ascii=False))
#         return file_dict
#
#     def __get_locked_filename(self, ui_all_filename,continuous_filename_time):
#         locked_file =[]
#         print("***TEST20.0***")
#         #remove unlocked continuous file
#         if not continuous_filename_time:
#             print("***TEST20***")
#             print(locked_file)
#             print("***TEST21***")
#
#
#             return locked_file
#         else:
#             print("***TEST22.0*!**")
#
#             print(ui_all_filename)
#             for i in ui_all_filename:
#                 print("***TEST22.1***")
#                 if self.__compare_time(i[0],i[1],i[2],continuous_filename_time) ==1:
#                     print("***TEST22.2***")
#                     locked_file.append(i[0])
#
#
#             print("***TEST23!!!!!!!!!***")
#             print(locked_file)
#             print("***TEST24***")
#             return locked_file
#
#
#     def __compare_time(self, name, start, finish ,continuous_filename_time):
#         #Theelement of list (str->int)
#
#         # python 3 style:
#         begin = list(map(int, start))
#         end   = list(map(int, finish))
#         continuous = continuous_filename_time
#
#         print("0000\n")
#         print(continuous_filename_time)
#         print("000001111\n")
#
#
#         #return locked,0:file unlocked, 1:file locked
#         locked = 0
#         gmt_time = datetime.timedelta(hours = 8)
#         for i in range(len(continuous)):
#             file_begintime = datetime.datetime(begin[0], begin[1], begin[2], begin[3], begin[4], begin[5], begin[6])
#
#
#             # print("0!!\n")
#             continuous_file_begintime = datetime.datetime(int(continuous[i][1][0]), int(continuous[i][1][1]), int(continuous[i][1][2]), int(continuous[i][1][3]), int(continuous[i][1][4]), int(continuous[i][1][5]), int(continuous[i][1][6]))+gmt_time
#             # print("1!\n")
#             # print(continuous_file_begintime)
#             # print("2!\n")
#
#
#             begin_edge = file_begintime - continuous_file_begintime
#
#             file_endtime = datetime.datetime(end[0], end[1], end[2], end[3], end[4], end[5], end[6])
#             continuous_file_endtime = datetime.datetime(int(continuous[i][2][0]), int(continuous[i][2][1]), int(continuous[i][2][2]), int(continuous[i][2][3]), int(continuous[i][2][4]), int(continuous[i][2][5]), int(continuous[i][2][6]))+gmt_time
#             end_edge = file_endtime - continuous_file_endtime
#
#             if begin_edge.total_seconds() >= 0.0 and end_edge.total_seconds() <= 0.0 :
#                 locked = 1
#             else :
#                 pass
#
#         return locked




# ------------------------------------------------------------------

class Sdrecordingfile(object):
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




    def get_ftp_all_filename(self):
        """Get all recording file from SD card."""
        tn = TelnetModule(self.ip, self.account, self.password).login().send_command('find /mnt/auto/CF/NCMF -name "*.mp4"')
        # tn = TelnetModule(self.ip, self.account, self.password).login().send_command('find /mnt/auto/CF/NCMF -name "*medium_stress*.mp4"')

        filename =  re.findall(b"NCMF\D(.*)",tn.result()[0])

        for i in range(len(filename)):
            filename[i] = filename[i].strip()
        # filename.remove("-name \"*medium_stress*.mp4\"")
        filename.remove(b"-name \"*.mp4\"")
        return filename

    def get_ui_all_filename(self):
        """Get all recording file from UI by cgi."""
        command = 'http://'+self.ip+'/cgi-bin/admin/lsctrl.cgi?cmd=search'
        url = URI.set(command, self.account, self.password)
        data = url.read()
        filename = re.findall(b"NCMF\D\D(.*)<",data)
        file_starttime =  re.findall(b"beginTime>(.*)<",data)
        file_endtime   =  re.findall(b"endTime>(.*)<",data)
        all_file=[]

        #all_file : [filename,starttime,file_endtime]
        for i in range(len(filename)):
            all_file.append([filename[i], file_starttime[i], file_endtime[i]])

        # print "++++"
        # print all_file
        # print "++++"
        #TO DO:for datetime format
        #'2016-04-01 00:44:56.637'
        #['2016', '04', '01', '00', '44', '56', '637']
        for i in range(len(all_file)):
            for j in range(1,len(all_file[0]),1):
                all_file[i][j] = re.split(b'-| |:|\.',all_file[i][j])



        return all_file

    def continuous_filename_time(self):
        """Get locked continuous_filename begin time and end time."""
        restart_status = 0
        locked_file = self.__get_continuous_locked_filename_time()

        print("***\n")
        print(locked_file)
        print("****\n")

        for file in locked_file:
            #index = 2 ,that is file endtime
            #if file[2] is None,stop recording
            if not file[2]:
                restart_status = 1
                self.__restart_recording()

        if restart_status == 0:
            return self.__process_continuous_filename(locked_file)
        else :
            return 'restart'

    def __get_continuous_locked_filename_time(self):
        """Get locked continuous_filename begin time and end time."""
        command = 'http://'+self.ip+'/cgi-bin/admin/lsctrlrec.cgi?cmd=getSlices'
        url = URI.set(command, self.account, self.password)
        data = url.read()
        islocked = re.findall(b"<islocked>(\d)",data)
        lockedfile_starttime = re.findall(b"sliceStart>(.*)<",data)
        lockedfile_endtime   = re.findall(b"sliceEnd>(.*)<",data)
        lockedfile = []

        #remove unlocked file info (isLocked = 0)
        #lockedfile = [islocked,starttime,endtime] = ['1', '2016-03-31T16:44:56.637Z', '2016-03-31T16:46:23.583Z']
        for i in range(len(islocked)):
            if  islocked[i] != b'0' :
                lockedfile.append([islocked[i], lockedfile_starttime[i], lockedfile_endtime[i]])
        return lockedfile

    def __restart_recording(self):
        """Restart camera by cgi"""
        command = 'http://'+self.ip+'/cgi-bin/admin/setparam.cgi?recording_i0_enable=0'
        URI.set(command, self.account, self.password)
        time.sleep(3)
        command = 'http://'+self.ip+'/cgi-bin/admin/setparam.cgi?recording_i0_enable=1'
        URI.set(command, self.account, self.password)
        #avoid to blank info
        time.sleep(10)

    def __process_continuous_filename(self,data):
        """Process continuous filename contrast to datetime"""
        file_time = data
        #['1', '2016-03-31T16:44:56.637Z', '2016-03-31T16:46:23.583Z']
        #['1', ['2016', '03', '31', '16', '44', '56', '637'], ['2016', '03', '31', '16', '46', '23', '583']]
        for file in range(len(file_time)):
            for time in range(1,len(file_time[0]),1):
                file_time[file][time] = re.split(b'-|T|:|\.|Z',file_time[file][time])
                #remove blank element
                file_time[file][time] = [_f for _f in file_time[file][time] if _f]
        return file_time

    def get_fw_file_dict(self):
        # try:
        #     command = 'http://'+self.ip+'/cgi-bin/admin/lsctrlrec.cgi?cmd=getSlices'
        #     URI.set(command, self.account, self.password)
        #     self.get_new_fw_file_dict()
        # except:
        #     self.get_old_fw_file_dict()

        command = 'http://'+self.ip+'/cgi-bin/admin/lsctrlrec.cgi?cmd=getSlices'
        URI.set(command, self.account, self.password)
        self.get_new_fw_file_dict()


    def get_old_fw_file_dict(self):
        print("TESTold")

        file_dict={}
        unlocked_file =[]
        ftp_all_filename = self.get_ftp_all_filename()

        command = 'http://'+self.ip+'/cgi-bin/admin/lsctrl.cgi?cmd=search&isLocked=1'
        url = URI.set(command, self.account, self.password)
        data = url.read()
        locked_file = re.findall(b"NCMF\D\D(.*)<",data)

        #remove event recording
        for file_name in ftp_all_filename:
            if b'event'in file_name:
                ftp_all_filename.remove(file_name)

        #compare ftp_all_filename,remove FW fake recording (FW-Bug)
        for file_name in locked_file:
            if file_name not in ftp_all_filename:
                locked_file.remove(file_name)

        for file_name in ftp_all_filename:
            if file_name not in locked_file:
                unlocked_file.append(file_name)


        file_dict["all_file"] = [x.decode() for x in ftp_all_filename]
        file_dict["locked_file"] = [x.decode() for x in locked_file]
        file_dict["unlocked_file"] = [x.decode() for x in unlocked_file]

        print(json.dumps(file_dict, ensure_ascii=False))
        return file_dict


    def get_new_fw_file_dict(self):
        """Return recording files by categories in dictionary
        Key1 : all_file ;
        Key2 : locked_file;
        Key3 : unlocked_file;
        """
        print("TESTnew")
        file_dict={}
        ftp_all_filename = self.get_ftp_all_filename()
        ui_all_filename =self.get_ui_all_filename()
        while 1:
            continuous_filename_time = self.continuous_filename_time()
            if continuous_filename_time != 'restart':
                break

        print("-----------------------------")
        print(continuous_filename_time)
        print("-----------------------------")

        locked_file = self.__get_locked_filename(ui_all_filename, continuous_filename_time)

        unlocked_file =[]

        #remove event recording
        for file_name in ftp_all_filename:
            if b'event'in file_name:
                ftp_all_filename.remove(file_name)

        #compare ftp_all_filename,remove FW fake recording (FW-Bug)
        for file_name in locked_file:
            if file_name not in ftp_all_filename:
                locked_file.remove(file_name)

        for file_name in ftp_all_filename:
            if file_name not in locked_file:
                unlocked_file.append(file_name)


        file_dict["all_file"] = [x.decode() for x in ftp_all_filename]
        file_dict["locked_file"] = [x.decode() for x in locked_file]
        file_dict["unlocked_file"] = [x.decode() for x in unlocked_file]

        print(json.dumps(file_dict, ensure_ascii=False))
        return file_dict

    def __get_locked_filename(self, ui_all_filename,continuous_filename_time):
        locked_file =[]
        #remove unlocked continuous file
        if not continuous_filename_time:

            print("**TEST1!**")

            return locked_file
        else:
            print("**TEST2**")
            print("XD")
            print(ui_all_filename)
            print("-----")
            for i in ui_all_filename:

                if self.__compare_time(i[0],i[1],i[2],continuous_filename_time) ==1:
                    locked_file.append(i[0])
                    print(locked_file)
            return locked_file


    def __compare_time(self, name, start, finish ,continuous_filename_time):
        #Theelement of list (str->int)
        begin = list(map(int, start))
        end   = list(map(int, finish))
        continuous = continuous_filename_time

        # print("TEST3!!!")

        # TEST = []
        # for i in continuous:
        #     if type(i) == list:
        #         print("**/LIST!**")
        #         print(i)
        #         print("LISTEND")
        #         # TEST[i] = [x.decode() for x in continuous[i]]
        #     else:
        #         print(i)


        print("BB\n")
        print(continuous_filename_time)
        # print(TEST)
        print(begin)
        print(end)
        print("EE!")

        #return locked,0:file unlocked, 1:file locked
        locked = 0
        gmt_time = datetime.timedelta(hours = 8)
        for i in range(len(continuous)):
            file_begintime = datetime.datetime(begin[0], begin[1], begin[2], begin[3], begin[4], begin[5], begin[6])
            # print("TEST4\n")
            # print(file_begintime)

            continuous_file_begintime = datetime.datetime(int(continuous[i][1][0]), int(continuous[i][1][1]), int(continuous[i][1][2]), int(continuous[i][1][3]), int(continuous[i][1][4]), int(continuous[i][1][5]), int(continuous[i][1][6]))+gmt_time
            #
            # print("TEST5\n")
            # print(continuous_file_begintime)


            begin_edge = file_begintime - continuous_file_begintime

            # print("TEST6\n")
            # print(begin_edge)

            file_endtime = datetime.datetime(end[0], end[1], end[2], end[3], end[4], end[5], end[6])
            # print("TEST7\n")
            # print(file_endtime)

            continuous_file_endtime = datetime.datetime(int(continuous[i][2][0]), int(continuous[i][2][1]), int(continuous[i][2][2]), int(continuous[i][2][3]), int(continuous[i][2][4]), int(continuous[i][2][5]), int(continuous[i][2][6]))+gmt_time
            # print("TEST8\n")
            # print(continuous_file_endtime)

            end_edge = file_endtime - continuous_file_endtime
            # print("TEST9!\n")
            # print(end_edge)

            if begin_edge.total_seconds() >= 0.0 and end_edge.total_seconds() <= 0.0 :
                locked = 1
            else :
                pass

        # print("LOCK!\n")
        # print(locked)
        # print("LOCKED\n")


        return locked

