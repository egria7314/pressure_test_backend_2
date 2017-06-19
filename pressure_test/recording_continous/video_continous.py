from django.shortcuts import render
import os, re, datetime,shutil
from django.shortcuts import render
from rest_framework.response import Response
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated

# from pressure_test.camera_log.sd_status import SDstatus
from recording_continous.models import RecordingContinuty

class VideoContinous(object):
    def __init__(self,video_before, video_now):
        self.directory_path = os.path.dirname(os.path.realpath(__file__))
        self.mp4parser_path = os.path.join(self.directory_path, "Mpeg4Parser_TimeParser.exe")
        self.video_before = video_before
        self.video_now  = video_now
        self.delay_time = 1


    def continuity_bwtween_recording_files(self):
        # video_path_before = os.path.join(self.directory_path, self.video_before)
        # video_path_now = os.path.join(self.directory_path, self.video_now)
        video_path_before = self.video_before
        video_path_now = self.video_now

        log_file_before = video_path_before.replace(".mp4", "_log.txt")
        log_file_now = video_path_now.replace(".mp4", "_log.txt")

        self.__produce_video_log(self.mp4parser_path, video_path_before, log_file_before)
        self.__produce_video_log(self.mp4parser_path, video_path_now, log_file_now)

        time_list_before = self.__analyze_video_log(log_file_before)
        time_list_now = self.__analyze_video_log(log_file_now)
        if "Decode error" in time_list_before or "Decode error" in time_list_now :
            result_dictionary = {"between_result": "failed", "seconds": "Decode error"}

        else:
            if float(time_list_now[0]) - float(time_list_before[-1]) < 1 and float(time_list_before[0]) < float(time_list_now[0]):
                analyze_result ='pass'
                delay_second = '-'
            else:
                analyze_result = 'failed'
                delay_second = str(float(time_list_now[0]) - float(time_list_before[-1]))

            result_dictionary ={"between_result": analyze_result, "seconds": delay_second}

        return result_dictionary


    def continuity_in_recording_files(self):
        # Todo : Change video_path from NAS_path
        # video_path = os.path.join(self.directory_path, self.video_now)
        video_path = self.video_now
        log_file = video_path.replace(".mp4","_log.txt")
        self.__produce_video_log(self.mp4parser_path, video_path, log_file)
        time_list = self.__analyze_video_log(log_file)
        time_delay=[]
        if "Decode error" in time_list :
            analyze_result = 'failed'
            start_time = '-'
            end_time = '-'
            error_code = 'Decode error'
            link = "-"
            count = "-"
        else:
            for i in range(len(time_list)-1):
                before = float(time_list[i])
                now = float(time_list[i+1])
                if now - before > self.delay_time:
                    time_delay.append([before, now, now - before])

            lag_number = 0
            if time_delay != []:
                self.__produe_failed_detail(time_delay)
                for index, value in enumerate(time_delay):
                    if float(value[2] > lag_number): lag_number = index
                time_delay[lag_number][0] = str(datetime.datetime.fromtimestamp(time_delay[lag_number][0]))
                time_delay[lag_number][1] = str(datetime.datetime.fromtimestamp(time_delay[lag_number][1]))
                time_delay[lag_number][2] = str(time_delay[lag_number][2])
                analyze_result = 'failed'
                start_time = time_delay[lag_number][0]
                end_time = time_delay[lag_number][1]
                error_code = 'error'
                link = self.video_now
                count = str(len(time_delay))
            else:
                analyze_result = 'pass'
                start_time = '-'
                end_time = '-'
                error_code = '-'
                link="-"
                count ='-'

        result_dictionary ={"creat_at":"19900603", "video_path":self.video_now, "size":"9487",
                            "in_result":analyze_result, "error_code":error_code, "start_time":start_time,
                            "end_time":end_time, "link":link, "count":count
                            }

        return result_dictionary


    def __produce_video_log(self, mp4parser, video_path, log_file):
        com_array = ["wine {0} -p {1} -t 3 > {2}".format(mp4parser, video_path, log_file)]
        print (com_array)
        batch_command = ''
        for command in com_array:
            batch_command = batch_command+command+";"

        print ('*******************')
        print ('*******************')
        print (batch_command)
        print ('*******************')
        print ('*******************')

        os.system(batch_command)


    def __analyze_video_log(self, video_log_path):
        time_list=[]
        video_log = open(video_log_path, "r").readlines()
        for i in video_log:
            if "Stream" in i :
                try:
                    time = re.search("Stream:(JPEG|H264|H265)\s+Frame:(I|P)\s+(\d+.\d+)", i).group(3)
                    time_list.append(time)
                except Exception as e:
                    # raise Exception("Video decode error: {}".format(video_log_path))
                    pass
        if time_list == []:
            time_list = ["Decode error"]
        return time_list

    def __produe_failed_detail(self, time_delay_list):
        error_info_folder = os.path.join(os.path.dirname(self.video_now),"continous_error")
        if not os.path.isdir(error_info_folder):
            os.mkdir(error_info_folder)

        txt_name = (os.path.basename(self.video_now)).split(".")
        txt_name[1] = '.txt'
        error_info_file_name =''.join(txt_name)
        error_info_file_path = os.path.join(error_info_folder,"error_{0}".format(error_info_file_name))

        # print ('////////////////////')
        # print ('////////////////////')
        # print ('error_info_folder : {0}'.format(error_info_folder))
        # print ('error_info_file_path : {0}'.format(error_info_file_path))
        # print ('////////////////////')
        # print ('////////////////////')

        f = open(error_info_file_path, 'w')
        for i in time_delay_list:
            f.write('******************************************\n')
            # f.write('start_time:'+str(i[0]) + '\n')
            # f.write('end_time  :'+str(i[1])+'\n')
            # f.write('delay_time:'+str(i[2]) + '\n')
            f.write('start_time:'+str(datetime.datetime.fromtimestamp(i[0]))+'\n')
            f.write('end_time  :'+str(datetime.datetime.fromtimestamp(i[1]))+'\n')
            f.write('delay_time:'+str(i[2]) + '\n')
            f.write('******************************************\n')
        f.close()
