__author__ = 'carlos.hu'
# -*- coding: utf-8 -*-
import re
import os
import json
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
        nas_info = {}
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
            nas_info['nasPath'] = nas_location
            nas_info['comment'] = ''

            return nas_info
        except:
            nas_info['loaction'] = ''
            nas_info['comment'] = 'NAS setting failed'
            return nas_info

    def get_video2(self, remote_username, remote_password, sudo_password, remote_path, prefix, time_start=0, time_end=0):
        """
        """

        # get nas location
        # remote_path = '\\\\172.19.11.191\\Oliver\\NAS\\medium_stress'.replace('\\','/')
        # prefix = "medium_stress"
        # remote_path = '\\\\172.19.11.189\\Public\\autotest\\NAS\\debug'.replace('\\','/')
        # remote_path = self.get_nas_location().replace('\\','/')
        if 'failed' in remote_path:
            raise Exception('getting NAS location failed')

        local_path = os.path.join("/mnt", remote_path.replace('//', '').replace('/', '_'))

        # walk through hierarchical
        self.mount_folder(
            remote_username=remote_username,
            remote_password=remote_password,
            remote_path=remote_path,
            sudo_password=sudo_password,
            local_path=local_path)

        videos = self.dump_nas_files(remote_path, prefix, time_start, time_end)
        print ('type(videos) = {0}'.format(type(videos)))
        # unmount
        self.unmount_folder(local_path, sudo_password)

        return videos

    def dump_nas_files(self, search_dir_web, prefix, timestamp_start, timestamp_end):
        """
        by mount command
        """
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
                    # file.append(os.path.join(search_dir_web, possible_file.groups()[0]))
                    file_local[file_path] = file_mod_time
                    file_web[os.path.join(search_dir_web, possible_file.groups()[0])] = [file_mod_time, file_size]
                    file_path_map[file_path] = os.path.join(search_dir_web, possible_file.groups()[0])
        sorted_file = sorted(file_local.items(), key=operator.itemgetter(1))
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
        p.expect(': ')
        p.sendline(sudo_password)
        p.expect( "\r\n" )

        # mount
        cmd = "sudo mount -t cifs -o username={user},password={pwd} {remote_path} {local_path}".format(
            user=remote_username, pwd=remote_password,
            remote_path=remote_path, local_path=local_path)

        p = pexpect.spawn(cmd)
        p.expect(': ')
        p.sendline(sudo_password)
        p.expect( "\r\n" )

        # wait mounting
        time.sleep(10)

    def unmount_folder(self, local_path, sudo_password):
        """
        """
        if platform.system() == 'Windows': return

        # umount
        cmd = "sudo umount {local_path}".format(local_path=local_path)
        p = pexpect.spawn(cmd)
        p.expect(': ')
        p.sendline(sudo_password)
        p.expect( "\r\n" )

        # remove folder
        time.sleep(10)
        if not os.path.ismount(local_path):
            cmd = "sudo rm -rf {mounted_at}".format(mounted_at=local_path)
            p = pexpect.spawn(cmd)
            p.expect(': ')
            p.sendline(sudo_password)
            p.expect( "\r\n" )

        if os.path.exists(local_path): return False

        return True


if __name__ == "__main__":
    import sys
    camera_ip = sys.argv[1]
    camera_name = sys.argv[2]
    camera_password = sys.argv[3]
    sudo_password = sys.argv[4]
    nas_username = sys.argv[5]
    nas_password = sys.argv[6]
    prefix = "medium_stress"
    remote_path = '\\\\172.19.11.189\\Public\\autotest\\NAS\\debug'.replace('\\','/')


    # myNasStorage = NasStorage(camera_ip,camera_name,camera_password, nas_username, nas_password)
    # # myNasStorage.get_video()
    # # nas_username = myNasStorage.get_nas_username()
    # # nas_password = myNasStorage.get_nas_password()
    # myNasStorage.get_video2(nas_username, nas_password, sudo_password)
    # # myNasStorage = NasStorage('172.19.16.126', 'root', '1')
    # # myNasStorage.get_video2("autotest", "autotest", "123")
    myNasStorage = NasStorage(nas_username, nas_password)
    print (myNasStorage.get_nas_location(camera_ip, camera_name, camera_password))
    print (myNasStorage.get_video2(nas_username, nas_password, sudo_password))
