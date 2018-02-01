# -*- coding: utf-8 -*-
import re
import os
import platform
import time
import operator
import datetime
from libs.pressure_test_logging import PressureTestLogging as ptl
from libs.storage import Storage

class VastStorage(Storage):

    def get_video_vast(self, remote_username, remote_password, sudo_password, remote_path, time_start, time_end, camera_log_tag=None):
        """
        """
        ptl.logging_info('start get_video_vast({0}, {1}, {2}, {3}, {4}, {5})'.format(remote_username, remote_password, sudo_password, remote_path, time_start, time_end))
        delta = time_end - time_start
        date_list = []
        for i in range(delta.days + 1):
            date_list.append((time_start + datetime.timedelta(days=i)).strftime('%Y-%m-%d'))
        if time_end.strftime('%Y-%m-%d') not in date_list:
            date_list.append(time_end.strftime('%Y-%m-%d'))
        videos = {}
        videos_info = {}
        for date in date_list:
            ptl.logging_info('DATE:  = {0}'.format(date))
            # print("DATE: ", date)
            remote_path = re.sub('\d{4}-\d{2}-\d{2}', '{0}', remote_path).format(date)
            local_path = os.path.join("/mnt", remote_path.replace('//', '').replace('/', '_'))
            ptl.logging_info('remote_path = {0}'.format(remote_path))
            ptl.logging_info('local_path = {0}'.format(local_path))
            self.mount_folder(
                remote_username=remote_username,
                remote_password=remote_password,
                remote_path=remote_path,
                sudo_password=sudo_password,
                local_path=local_path)

            ptl.logging_info('self.mount_folder({0}, {1}, {2}, {3}, {4})'.format(remote_username, remote_password, remote_path, sudo_password, local_path))
            timestamp_start = time.mktime(time_start.timetuple())
            timestamp_end = time.mktime(time_end.timetuple())
            if camera_log_tag != None:
                video, videos_info = self.dump_storage_files(remote_path, timestamp_start, timestamp_end, camera_log_tag=camera_log_tag)
                videos_info.update(videos_info)
            else:
                video = self.dump_storage_files(remote_path, timestamp_start, timestamp_end, camera_log_tag=camera_log_tag)
            videos.update(video)
            # # unmount
            # self.unmount_folder(local_path, sudo_password)

        ptl.logging_info('return videos = {0}'.format(videos))
        if camera_log_tag != None:
            videos_copy = videos.copy()
            for k in videos.keys():
                if 'verify_storage.checked' in k:
                    videos_copy.pop(k, None)
                    return videos_copy, videos_info, True
            return videos, videos_info, False
        return videos




