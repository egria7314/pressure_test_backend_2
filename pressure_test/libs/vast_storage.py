# -*- coding: utf-8 -*-
import re
import os
import pexpect
import platform
import time
import operator
import datetime

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

    def get_video_vast(self, remote_username, remote_password, sudo_password, remote_path, time_start=0, time_end=0):
        """
        """
        start_date_detail = datetime.datetime.fromtimestamp(time_start)
        start_date_obj = datetime.date(int(start_date_detail.strftime('%Y')), int(start_date_detail.strftime('%m')), int(start_date_detail.strftime('%d')))
        end_date_detail = datetime.datetime.fromtimestamp(time_start)
        end_date_obj = datetime.date(int(end_date_detail.strftime('%Y')), int(end_date_detail.strftime('%m')), int(end_date_detail.strftime('%d')))

        delta = end_date_obj - start_date_obj
        date_list = []
        for i in range(delta.days + 1):
            date_list.append((start_date_obj + datetime.timedelta(days=i)).strftime('%Y-%m-%d'))
        videos = {}
        for date in date_list:
            remote_path = re.sub('\d{4}-\d{2}-\d{2}', '{0}', remote_path).format(date)
            if 'failed' in remote_path:
                raise Exception('getting VAST location failed')

            local_path = os.path.join("/mnt", remote_path.replace('//', '').replace('/', '_').replace('.', '_'))
            self.mount_folder(
                remote_username=remote_username,
                remote_password=remote_password,
                remote_path=remote_path,
                sudo_password=sudo_password,
                local_path=local_path)
            video = self.dump_vast_files(remote_path, time_start, time_end)
            videos.update(video)
            # unmount
            self.unmount_folder(local_path, sudo_password)

        return videos

    def dump_vast_files(self, search_dir_web, timestamp_start, timestamp_end):
        """
        by mount command
        """
        file_web = {}
        file_local = {}
        file_path_map = {}
        if platform.system() == 'Linux':
            search_dir = os.path.join("/mnt", search_dir_web.replace('//', '').replace('/', '_').replace('.', '_'))
        else:
            search_dir = search_dir_web
        for root, dirs, files in os.walk(search_dir):
            for f in files:
                file_path = os.path.join(root,f).replace('\\','/')
                file_mod_time = os.stat(file_path).st_mtime
                file_size = os.stat(file_path).st_size
                possible_file = re.search(search_dir + '/(.*3gp)', file_path)
                if possible_file and file_mod_time > timestamp_start and file_mod_time < timestamp_end:
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
    # myNasStorage = VastStorage(nas_username, nas_password)
    # print (myNasStorage.get_nas_location(camera_ip, camera_name, camera_password))
    # print (myNasStorage.get_video2(nas_username, nas_password, sudo_password))
