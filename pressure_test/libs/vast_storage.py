# -*- coding: utf-8 -*-
import re
import os
import pexpect
import platform
import time
import operator
import datetime
from libs.pressure_test_logging import PressureTestLogging as ptl

class VastStorage(object):
    def __init__(self, vast_username=None, vast_password=None, domain='VIVOTEK'):
        """
        Keyword arguments:
        nas_username -- the string of nas username to login
        nas_password -- the string of nas password to login
        """
        self.vast_username = vast_username
        self.vast_password = vast_password
        self.domain = domain

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

            time.sleep(120)

            ptl.logging_info('self.mount_folder({0}, {1}, {2}, {3}, {4})'.format(remote_username, remote_password, remote_path, sudo_password, local_path))
            timestamp_start = time.mktime(time_start.timetuple())
            timestamp_end = time.mktime(time_end.timetuple())
            video = self.dump_vast_files(remote_path, timestamp_start, timestamp_end, camera_log_tag)
            videos.update(video)
            # # unmount
            # self.unmount_folder(local_path, sudo_password)

        return videos

    def dump_vast_files(self, search_dir_web, timestamp_start, timestamp_end, camera_log_tag=None):
        """
        by mount command
        """
        ptl.logging_info('start dump_vast_files({0}, {1}, {2})'.format(search_dir_web, timestamp_start, timestamp_end))
        file_web = {}
        file_local = {}
        file_path_map = {}
        if platform.system() == 'Linux':
            search_dir = os.path.join("/mnt", search_dir_web.replace('//', '').replace('/', '_'))
        else:
            search_dir = search_dir_web

        for root, dirs, files in os.walk(search_dir):
            ptl.logging_info('search_dir = {0}, root = {1}, dirs = {2}, files = {3}'.format(search_dir, root, dirs, files))
            for f in files:
                file_path = os.path.join(root,f).replace('\\','/')
                file_mod_time = os.stat(file_path).st_mtime
                file_size = os.stat(file_path).st_size
                possible_file = re.search(search_dir + '/(.*3gp)', file_path)
                if possible_file and file_mod_time > timestamp_start and file_mod_time < timestamp_end:
                    file_local[file_path] = file_mod_time
                    file_web[os.path.join(search_dir_web, possible_file.groups()[0])] = [file_mod_time, file_size]
                    file_path_map[file_path] = os.path.join(search_dir_web, possible_file.groups()[0])
                else:
                    ptl.logging_info('Filtered f = {0}, file_path = {1}, possible_file = {2}, timestamp_start = {3}, file_mod_time = {4}, timestamp_end = {5}'
                                     .format(f, file_path, possible_file, timestamp_start, file_mod_time, timestamp_end))

        ptl.logging_info('file_local = {0}'.format(file_local))
        ptl.logging_info('file_web = {0}'.format(file_web))
        ptl.logging_info('file_path_map = {0}'.format(file_path_map))
        sorted_file = sorted(file_local.items(), key=operator.itemgetter(1))
        ptl.logging_info('sorted_file = {0}'.format(sorted_file))

        if camera_log_tag == None:
            if len(sorted_file) != 0:
                last_file_path = sorted_file[-1][0]
                # last_file_size_prev = os.stat(last_file_path).st_size
                # time.sleep(10)
                # last_file_size_curr = os.stat(last_file_path).st_size
                # if last_file_size_curr != last_file_size_prev:
                #     remove_file_path = file_path_map[last_file_path]
                #     del file_web[remove_file_path]
                #     ptl.logging_info('remove_file_path = {0}'.format(remove_file_path))
                remove_file_path = file_path_map[last_file_path]
                del file_web[remove_file_path]
        else:
            ptl.logging_info('this is for camera_log check, without delete editing file, file_web = {0}'.format(file_web))

        ptl.logging_info('return file_web = {0}'.format(file_web))
        return file_web

    def mount_folder(self, remote_username, remote_password, remote_path, sudo_password, local_path):
        """
        """
        if platform.system() == 'Windows': return

        if os.path.ismount(local_path):
            ptl.logging_info('mount status of vast is complete')
            return

        # create the new folder
        cmd = "sudo mkdir {mounted_at}".format(mounted_at=local_path)
        p = pexpect.spawn(cmd)
        ptl.logging_info('cmd = {0}, console message is {1}'.format(cmd, p.read()))
        # p.expect(': ')
        # p.sendline(sudo_password)
        # p.expect( "\r\n" )

        # mount
        cmd = "sudo mount -t cifs -o username={user},password={pwd} {remote_path} {local_path}".format(
            user=remote_username, pwd=remote_password,
            remote_path=remote_path, local_path=local_path)

        p = pexpect.spawn(cmd)
        ptl.logging_info('cmd = {0}, console message is {1}'.format(cmd, p.read()))
        # p.expect(': ')
        # p.sendline(sudo_password)
        # p.expect( "\r\n" )

        # wait mounting
        time.sleep(10)

    def unmount_folder(self, local_path, sudo_password):
        """
        """
        if platform.system() == 'Windows': return

        # umount
        cmd = "sudo umount {local_path}".format(local_path=local_path)
        p = pexpect.spawn(cmd)
        ptl.logging_info('cmd = {0}, console message is {1}'.format(cmd, p.read()))
        # p.expect(': ')
        # p.sendline(sudo_password)
        # p.expect( "\r\n" )

        # remove folder
        time.sleep(10)
        if not os.path.ismount(local_path):
            cmd = "sudo rm -rf {mounted_at}".format(mounted_at=local_path)
            p = pexpect.spawn(cmd)
            ptl.logging_info('cmd = {0}, console message is {1}'.format(cmd, p.read()))
            # p.expect(': ')
            # p.sendline(sudo_password)
            # p.expect( "\r\n" )

        if os.path.exists(local_path): return False

        return True

