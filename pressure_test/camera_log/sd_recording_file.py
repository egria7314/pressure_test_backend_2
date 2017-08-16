# __author__ = 'steven.hsiao'
# # -*- coding: utf-8 -*-
import json
import re
from camera_log.telnet_module import TelnetModule
from camera_log.telnet_module import URI
from libs.pressure_test_logging import PressureTestLogging as ptl

import datetime
import time

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


    def get_ftp_all_filename(self, timeout=300):
        """Get all recording file from SD card."""

        try:
            tn = TelnetModule(self.ip, self.account, self.password, timeout).login().send_command('find /mnt/auto/CF/NCMF -name "*.mp4"')
            filename =  re.findall(b"NCMF\D(.*)",tn.result()[0])
            ptl.logging_debug('[DEBUG] get filename, [filename]:{0}'.format(filename))

            for i in range(len(filename)):
                filename[i] = filename[i].strip()
            # filename.remove("-name \"*medium_stress*.mp4\"")
            filename.remove(b"-name \"*.mp4\"")
            # print(filename)
        except Exception as e:
            ptl.logging_error('[Exception] get ftp all file name error, [Error msg]:{0}'.format(e))
            print(e)
            filename = [b"get ftp all file name error"]

        return filename

    def get_ui_all_filename(self, timeout=300):
        """Get all recording file from UI by cgi."""
        command = 'http://'+self.ip+'/cgi-bin/admin/lsctrl.cgi?cmd=search'
        url = URI.set(command, self.account, self.password, timeout)
        data = url.read()
        filename = re.findall(b"NCMF\D\D(.*)<",data)
        file_starttime =  re.findall(b"beginTime>(.*)<",data)
        file_endtime   =  re.findall(b"endTime>(.*)<",data)
        all_file=[]
        #all_file : [filename,starttime,file_endtime]
        for i in range(len(filename)):
            all_file.append([filename[i], file_starttime[i], file_endtime[i]])

        #TO DO:for datetime format
        #'2016-04-01 00:44:56.637'
        #['2016', '04', '01', '00', '44', '56', '637']

        for i in range(len(all_file)):
            for j in range(1,len(all_file[0]),1):
                all_file[i][j] = re.split(b'-| |:|\.',all_file[i][j])

        return all_file

    def continuous_filename_time(self, timeout=300):
        """Get locked continuous_filename begin time and end time."""
        restart_status = 0
        locked_file = self.__get_continuous_locked_filename_time(timeout)

        for file in locked_file:
            #index = 2 ,that is file endtime
            #if file[2] is None,stop recording
            if not file[2]:
                restart_status = 1
                self.__restart_recording(timeout)

        if restart_status == 0:
            return self.__process_continuous_filename(locked_file)
        else :
            return 'restart'

    def __get_continuous_locked_filename_time(self, timeout=300):
        """Get locked continuous_filename begin time and end time."""
        command = 'http://'+self.ip+'/cgi-bin/admin/lsctrlrec.cgi?cmd=getSlices'
        url = URI.set(command, self.account, self.password, timeout)
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

    def __restart_recording(self, timeout=300):
        """Restart camera by cgi"""
        command = 'http://'+self.ip+'/cgi-bin/admin/setparam.cgi?recording_i0_enable=0'
        URI.set(command, self.account, self.password, timeout)
        time.sleep(3)
        command = 'http://'+self.ip+'/cgi-bin/admin/setparam.cgi?recording_i0_enable=1'
        URI.set(command, self.account, self.password, timeout)
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

    def get_fw_file_dict(self, timeout=300):
        try:
            command = 'http://'+self.ip+'/cgi-bin/admin/lsctrlrec.cgi?cmd=getSlices'
            URI.set(command, self.account, self.password, timeout)
            return self.get_new_fw_file_dict(timeout)
        except:
            return self.get_old_fw_file_dict(timeout)


    def get_old_fw_file_dict(self, timeout=300):
        # print("TESTold")

        file_dict={}
        unlocked_file =[]
        ftp_all_filename = self.get_ftp_all_filename(timeout)

        command = 'http://'+self.ip+'/cgi-bin/admin/lsctrl.cgi?cmd=search&isLocked=1'
        url = URI.set(command, self.account, self.password, timeout)
        data = url.read()
        locked_file = re.findall(b"NCMF\D\D(.*)<",data)

        # #remove event recording
        # for file_name in ftp_all_filename:
        #     if b'event'in file_name:
        #         ftp_all_filename.remove(file_name)

        #compare ftp_all_filename,remove FW fake recording (FW-Bug)
        for file_name in locked_file:
            if file_name not in ftp_all_filename:
                locked_file.remove(file_name)

        for file_name in ftp_all_filename:
            if file_name not in locked_file:
                unlocked_file.append(file_name)


        file_dict["sd_all_file"] = [x.decode() for x in ftp_all_filename]
        file_dict["sd_locked_file"] = [x.decode() for x in locked_file]
        file_dict["sd_unlocked_file"] = [x.decode() for x in unlocked_file]

        # print(json.dumps(file_dict, ensure_ascii=False))
        return file_dict


    def get_new_fw_file_dict(self, timeout=300):
        """Return recording files by categories in dictionary
        Key1 : all_file ;
        Key2 : locked_file;
        Key3 : unlocked_file;
        """
        file_dict={}
        ftp_all_filename = self.get_ftp_all_filename(timeout)

        ui_all_filename =self.get_ui_all_filename(timeout)
        while 1:
            continuous_filename_time = self.continuous_filename_time(timeout)
            if continuous_filename_time != 'restart':
                break

        locked_file = self.__get_locked_filename(ui_all_filename, continuous_filename_time)
        unlocked_file =[]

        # #remove event recording
        # for file_name in ftp_all_filename:
        #     if b'event'in file_name:
        #         ftp_all_filename.remove(file_name)

        #compare ftp_all_filename,remove FW fake recording (FW-Bug)
        for file_name in locked_file:
            if file_name not in ftp_all_filename:
                locked_file.remove(file_name)

        for file_name in ftp_all_filename:
            if file_name not in locked_file:
                unlocked_file.append(file_name)

        file_dict["sd_all_file"] = [x.decode() for x in ftp_all_filename]
        file_dict["sd_locked_file"] = [x.decode() for x in locked_file]
        file_dict["sd_unlocked_file"] = [x.decode() for x in unlocked_file]

        # print(json.dumps(file_dict, ensure_ascii=False))
        return file_dict

    def __get_locked_filename(self, ui_all_filename,continuous_filename_time):
        locked_file =[]
        #remove unlocked continuous file
        if not continuous_filename_time:
            return locked_file
        else:
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

        #return locked,0:file unlocked, 1:file locked
        locked = 0
        gmt_time = datetime.timedelta(hours = 8)
        for i in range(len(continuous)):
            file_begintime = datetime.datetime(begin[0], begin[1], begin[2], begin[3], begin[4], begin[5], begin[6])
            continuous_file_begintime = datetime.datetime(int(continuous[i][1][0]), int(continuous[i][1][1]), int(continuous[i][1][2]), int(continuous[i][1][3]), int(continuous[i][1][4]), int(continuous[i][1][5]), int(continuous[i][1][6]))+gmt_time
            begin_edge = file_begintime - continuous_file_begintime
            file_endtime = datetime.datetime(end[0], end[1], end[2], end[3], end[4], end[5], end[6])
            continuous_file_endtime = datetime.datetime(int(continuous[i][2][0]), int(continuous[i][2][1]), int(continuous[i][2][2]), int(continuous[i][2][3]), int(continuous[i][2][4]), int(continuous[i][2][5]), int(continuous[i][2][6]))+gmt_time
            end_edge = file_endtime - continuous_file_endtime
            if begin_edge.total_seconds() >= 0.0 and end_edge.total_seconds() <= 0.0 :
                locked = 1
            else :
                pass

        return locked

