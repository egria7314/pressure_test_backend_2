__author__ = 'carlos.hu'
# -*- coding: utf-8 -*-
import re
import os
import platform
import time
import operator
from libs.storage import Storage
from libs.telnet_module import URI
from libs.pressure_test_logging import PressureTestLogging as ptl

class NasStorage(Storage):


    def get_nas_location(self, camera_ip, camera_name, camera_password):
        """Get nas location from camera by cgi"""
        nas_info = {"nasPath":'', 'info':[{'status': '', 'comment': '', 'action': ''}]}
        command = 'http://'+camera_ip+'/cgi-bin/admin/getparam.cgi?server_i0_type&server_i1_type&server_i2_type&&server_i3_type&server_i4_type&server_i5_type'
        try:
            url = URI.set(command, camera_name, camera_password)
            url = url.read().decode('utf-8').split("\r\n")
            for i in url:
                if 'ns' in i:
                    server_number = re.search("i(\d)_type",i).groups()[0]
            command = 'http://'+camera_ip+'/cgi-bin/admin/getparam.cgi?server_i'+str(server_number)+'_ns_location'
            url = URI.set(command, camera_name, camera_password)
            nas_location =  url.read().decode('utf-8')
            nas_location = re.search('\'(.*)\'',nas_location).groups()[0]
            nas_location = "\\" .join(nas_location.split('\\\\'))
            nas_info["nasPath"] = nas_location
            nas_info['info'][0]['status'] = 'success'
            nas_info['info'][0]['action'] = 'get_nas_location'

            return nas_info
        except:
            nas_info['info'][0]['status'] = 'fail'
            nas_info['info'][0]['action'] = 'get_nas_location'
            nas_info['info'][0]['comment'] = 'NAS setting failed'
            return nas_info


    def get_video_nas(self, remote_username, remote_password, sudo_password, remote_path, prefix, time_start, time_end, camera_log_tag=None):
        """
        """
        ptl.logging_info('start get_video_nas({0}, {1}, {2}, {3}, {4}, {5}, {6})'.format(remote_username, remote_password, sudo_password, remote_path, prefix, time_start, time_end))
        local_path = os.path.join("/mnt", remote_path.replace('//', '').replace('/', '_'))
        ptl.logging_info('mount local path = {0}'.format(local_path))
        # walk through hierarchical
        self.mount_folder(
            remote_username=remote_username,
            remote_password=remote_password,
            remote_path=remote_path,
            sudo_password=sudo_password,
            local_path=local_path)
        timestamp_start = time.mktime(time_start.timetuple())
        timestamp_end = time.mktime(time_end.timetuple())
        # # unmount
        # self.unmount_folder(local_path, sudo_password)

        if camera_log_tag != None:
            videos, videos_info = self.dump_storage_files(remote_path, timestamp_start, timestamp_end, 'nas', prefix, camera_log_tag=camera_log_tag)
            # ptl.logging_info('return videos = {0}'.format(videos))
            videos_copy = videos.copy()
            for k in videos.keys():
                if 'verify_storage.checked' in k:
                    videos_copy.pop(k, None)
                    return videos_copy, videos_info, True
            return videos, videos_info, False
        else:
            videos = self.dump_storage_files(remote_path, timestamp_start, timestamp_end, 'nas', prefix, camera_log_tag=camera_log_tag)
            # ptl.logging_info('return videos = {0}'.format(videos))
        return videos







if __name__ == '__main__':
    import datetime
    # ns = NasStorage('autotest', 'autotest')
    # timestamp_start = datetime.datetime.strptime('2017-09-29 21:00:00', '%Y-%m-%d %H:%M:%S')
    # print ('timestamp_start = {0}'.format(timestamp_start))
    # timestamp_end = datetime.datetime.strptime('2017-09-29 23:00:00', '%Y-%m-%d %H:%M:%S')
    # print ('timestamp_end = {0}'.format(timestamp_end))
    # videos, durations, result = ns.get_video_nas('dqaautotest', 'vvtkdqa', 'fftbato', '//172.19.16.108/autotest/autotest/For_temp_test/Pressure_test/', 'medium_clip', timestamp_start, timestamp_end, True)
    # print(videos)
    # print(durations)


