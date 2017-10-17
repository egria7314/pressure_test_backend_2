__author__ = 'carlos.hu'
# -*- coding: utf-8 -*-
import re
import os
import pexpect
import platform
import time
import operator
from libs.telnet_module import URI
from libs.pressure_test_logging import PressureTestLogging as ptl

class NasStorage(object):
    def __init__(self, nas_username=None, nas_password=None, domain='VIVOTEK'):
        """
        Keyword arguments:
        nas_username -- the string of nas username to login
        nas_password -- the string of nas password to login
        """
        self.nas_username = nas_username
        self.nas_password = nas_password
        self.domain = domain

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
        videos = self.dump_nas_files(remote_path, prefix, timestamp_start, timestamp_end, camera_log_tag)
        # # unmount
        # self.unmount_folder(local_path, sudo_password)


        ptl.logging_info('return videos = {0}'.format(videos))
        if camera_log_tag != None:
            for k in videos.keys():
                if 'verify_storage.checked' in k:
                    return videos, True
            return videos, False

        return videos

    def dump_nas_files(self, search_dir_web, prefix, timestamp_start, timestamp_end, camera_log_tag=None):
        """
        by mount command
        """
        ptl.logging_info('start dump_nas_files({0}, {1}, {2}, {3})'.format(search_dir_web, prefix, timestamp_start, timestamp_end))
        # file = []
        file_web = {}
        file_local = {}
        file_path_map = {}
        if platform.system() == 'Linux':
            search_dir = os.path.join("/mnt", search_dir_web.replace('//', '').replace('/', '_'))
        else:
            search_dir = search_dir_web
        ptl.logging_info('search_dir_web = {0}'.format(search_dir))
        for root, dirs, files in os.walk(search_dir):
            for f in files:
                file_path = os.path.join(root,f).replace('\\','/')
                file_mod_time = os.stat(file_path).st_mtime
                file_size = os.stat(file_path).st_size
                possible_file = re.search(search_dir + '/(.*\.mp4)', file_path)
                checked_file = re.search(search_dir + '/(.*\.checked)', file_path)
                if possible_file and prefix in possible_file.groups()[0] and file_mod_time > timestamp_start and file_mod_time < timestamp_end:
                    file_local[file_path] = file_mod_time
                    file_web[os.path.join(search_dir_web, possible_file.groups()[0])] = [file_mod_time, file_size]
                    file_path_map[file_path] = os.path.join(search_dir_web, possible_file.groups()[0])
                elif checked_file and camera_log_tag != None:
                    file_web[os.path.join(search_dir_web, checked_file.groups()[0])] = [file_mod_time, file_size]
        # ptl.logging_info('file_local = {0}'.format(file_local))
        # ptl.logging_info('file_web = {0}'.format(file_web))
        # ptl.logging_info('file_path_map = {0}'.format(file_path_map))
        sorted_file = sorted(file_local.items(), key=operator.itemgetter(1))
        # ptl.logging_info('sorted file_local = {0}'.format(sorted_file))

        if camera_log_tag == None:
            if len(sorted_file) > 0:

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
            # ptl.logging_info('this is for camera_log check, without delete editing file, file_web = {0}'.format(file_web))
            pass
        # ptl.logging_info('return file_web = {0}'.format(file_web))
        return file_web

    def mount_folder(self, remote_username, remote_password, remote_path, sudo_password, local_path):
        """
        """
        if platform.system() == 'Windows': return

        if os.path.ismount(local_path):
            ptl.logging_info('mount status of nas is complete')
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

if __name__ == '__main__':
    import datetime
    ns = NasStorage('autotest', 'autotest')
    timestamp_start = datetime.datetime.strptime('2017-06-28 21:00:00', '%Y-%m-%d %H:%M:%S')
    print ('timestamp_start = {0}'.format(timestamp_start))
    timestamp_end = datetime.datetime.strptime('2017-06-30 23:00:00', '%Y-%m-%d %H:%M:%S')
    print ('timestamp_end = {0}'.format(timestamp_end))
    # timestamp_start = datetime.datetime.strptime('2017-06-28 21:00:00', '%Y-%m-%d %H:%M:%S')
    # timestamp_end = datetime.datetime.strptime('2017-06-30 23:00:00', '%Y-%m-%d %H:%M:%S')
    print(ns.get_video_nas('autotest', 'autotest', 'fftbato', '//172.19.11.189/Public/autotest/steven/', 'high_stress', timestamp_start, timestamp_end))


