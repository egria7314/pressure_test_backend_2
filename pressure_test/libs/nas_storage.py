__author__ = 'carlos.hu'
# -*- coding: utf-8 -*-
import re
import os
import pexpect
import platform
import time
import operator
from libs.telnet_module import URI

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


    def get_video_nas(self, remote_username, remote_password, sudo_password, remote_path, prefix, time_start, time_end):
        """
        """
        local_path = os.path.join("/mnt", remote_path.replace('//', '').replace('/', '_'))

        # walk through hierarchical
        self.mount_folder(
            remote_username=remote_username,
            remote_password=remote_password,
            remote_path=remote_path,
            sudo_password=sudo_password,
            local_path=local_path)
        timestamp_start = time.mktime(time_start.timetuple())
        timestamp_end = time.mktime(time_end.timetuple())
        videos = self.dump_nas_files(remote_path, prefix, timestamp_start, timestamp_end)
        # unmount
        # self.unmount_folder(local_path, sudo_password)

        return videos

    def dump_nas_files(self, search_dir_web, prefix, timestamp_start, timestamp_end):
        """
        by mount command
        """
        print("search_dir_web: ", search_dir_web )
        print("prefix: ", prefix)
        print("timestamp_start: ", timestamp_start)
        print("timestamp_end: ", timestamp_end)
        # file = []
        file_web = {}
        file_local = {}
        file_path_map = {}
        if platform.system() == 'Linux':
            search_dir = os.path.join("/mnt", search_dir_web.replace('//', '').replace('/', '_'))
        else:
            search_dir = search_dir_web
        for root, dirs, files in os.walk(search_dir):
            for f in files:
                file_path = os.path.join(root,f).replace('\\','/')
                file_mod_time = os.stat(file_path).st_mtime
                file_size = os.stat(file_path).st_size
                possible_file = re.search(search_dir + '/(.*mp4)', file_path)
                if possible_file and prefix in possible_file.groups()[0] and file_mod_time > timestamp_start and file_mod_time < timestamp_end:
                    file_local[file_path] = file_mod_time
                    file_web[os.path.join(search_dir_web, possible_file.groups()[0])] = [file_mod_time, file_size]
                    file_path_map[file_path] = os.path.join(search_dir_web, possible_file.groups()[0])
        sorted_file = sorted(file_local.items(), key=operator.itemgetter(1))
        print("sorted_file= ", sorted_file)
        if len(sorted_file) > 0:
            last_file_path = sorted_file[-1][0]
            last_file_size_prev = os.stat(last_file_path).st_size
            time.sleep(3)
            last_file_size_curr = os.stat(last_file_path).st_size
            if last_file_size_curr != last_file_size_prev:
                remove_file_path = file_path_map[last_file_path]
                del file_web[remove_file_path]

        return file_web

    def mount_folder(self, remote_username, remote_password, remote_path, sudo_password, local_path):
        """
        """
        if platform.system() == 'Windows': return

        if os.path.ismount(local_path): return

        # create the new folder
        cmd = "sudo mkdir {mounted_at}".format(mounted_at=local_path)
        p = pexpect.spawn(cmd)
        # p.expect(': ')
        # p.sendline(sudo_password)
        # p.expect( "\r\n" )

        # mount
        cmd = "sudo mount -t cifs -o username={user},password={pwd} {remote_path} {local_path}".format(
            user=remote_username, pwd=remote_password,
            remote_path=remote_path, local_path=local_path)

        p = pexpect.spawn(cmd)
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
        # p.expect(': ')
        # p.sendline(sudo_password)
        # p.expect( "\r\n" )

        # remove folder
        time.sleep(10)
        if not os.path.ismount(local_path):
            cmd = "sudo rm -rf {mounted_at}".format(mounted_at=local_path)
            p = pexpect.spawn(cmd)
            # p.expect(': ')
            # p.sendline(sudo_password)
            # p.expect( "\r\n" )

        if os.path.exists(local_path): return False

        return True


