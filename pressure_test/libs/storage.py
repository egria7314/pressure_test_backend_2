
import re
import subprocess
import re
import os
import pexpect
import platform
import time
import operator
import datetime
from libs.pressure_test_logging import PressureTestLogging as ptl

class Storage(object):

    def __init__(self, storage_username=None, storage_password=None, domain='VIVOTEK'):
        """
        Keyword arguments:
        storage_username -- the string of nas username to login
        storage_password -- the string of nas password to login
        """
        self.storage_username = storage_username
        self.storage_password = storage_password
        self.domain = domain


    def duration_to_second(self, duration):
        re_result = re.search(b'(\d+):(\d+):(\d+)', duration)
        try:
            hour = int(re_result.group(1))
            min = int(re_result.group(2))
            sec = int(re_result.group(3))
            return hour*60*60 + min*60 +sec
        except Exception as e:
            ptl.logging_info('Duration {0} transform error :{1}'.format(duration, e))
            raise e



    def get_duration_by_file_path(self, file_path):
        result = subprocess.Popen(["ffprobe", file_path],
                                  stdout= subprocess.PIPE, stderr=subprocess.STDOUT)
        for x in result.stdout.readlines():
            if b"Duration" in x:
                duration = re.search(b'Duration:\s([^,]+)', x).group(1)
                return self.duration_to_second(duration)
        # return [x for x in result.stdout.readlines() if b"Duration" in x]

    def get_file_size_by_file_path(self, file_path):

        size = os.path.getsize(file_path)

        return int(size/1024.0/1024.0) # return MB

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
        ## for local run
        # p.expect(': ')
        # p.sendline(sudo_password)
        # p.expect( "\r\n" )

        # mount
        cmd = "sudo mount -t cifs -o username={user},password={pwd} {remote_path} {local_path}".format(
            user=remote_username, pwd=remote_password,
            remote_path=remote_path, local_path=local_path)

        p = pexpect.spawn(cmd)
        ptl.logging_info('cmd = {0}, console message is {1}'.format(cmd, p.read()))
        ## for local run
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
        ## for local run
        # p.expect(': ')
        # p.sendline(sudo_password)
        # p.expect( "\r\n" )

        # remove folder
        time.sleep(10)
        if not os.path.ismount(local_path):
            cmd = "sudo rm -rf {mounted_at}".format(mounted_at=local_path)
            p = pexpect.spawn(cmd)
            ptl.logging_info('cmd = {0}, console message is {1}'.format(cmd, p.read()))
            ## for local run
            # p.expect(': ')
            # p.sendline(sudo_password)
            # p.expect( "\r\n" )

        if os.path.exists(local_path): return False

        return True

    def get_video_type_by_storage(self, type):
        if type == 'nas':
            return 'mp4'
        elif type == 'vast':
            return '3gp'
        else:
            raise Exception("Error storage type")

    def get_path_by_system(self, path):
        if platform.system() == 'Linux':
            return os.path.join("/mnt", path.replace('//', '').replace('/', '_'))
        else:
            return path

    def dump_storage_files(self, search_dir_web, timestamp_start, timestamp_end, type='vast', prefix='', camera_log_tag=None):
        '''
        
        :param search_dir_web: 
        :param timestamp_start: 
        :param timestamp_end: 
        :param type: nas/vast
        :param prefix: only supprot nas type
        :param camera_log_tag: 
        :return: 
        '''
        ptl.logging_info('start dump_{4}_files(search_dir_web:{0}, timestamp_start:{1}, timestamp_end:{2}, prefix:{3})'.format(search_dir_web,  timestamp_start,timestamp_end,prefix, type))
        file_web, file_info, file_local, file_path_map  = {}, {}, {}, {}

        search_dir = self.get_path_by_system(search_dir_web)

        ptl.logging_info('search_dir_web = {0}'.format(search_dir))

        for root, dirs, files in os.walk(search_dir):
            for f in files:
                file_path = os.path.join(root, f).replace('\\', '/')
                file_mod_time = os.stat(file_path).st_mtime
                file_size = os.stat(file_path).st_size

                possible_file = re.search(search_dir + '/(.*\.{0})'.format(self.get_video_type_by_storage(type)), file_path)
                checked_file = re.search(search_dir + '/(.*\.checked)', file_path)

                if possible_file and file_mod_time > timestamp_start and file_mod_time < timestamp_end and prefix in possible_file.groups()[0]:
                    file_local[file_path] = file_mod_time
                    storage_path = os.path.join(search_dir_web, possible_file.groups()[0])
                    file_web[storage_path] = [file_mod_time, file_size]
                    file_info[storage_path] = {"Duration": self.get_duration_by_file_path(file_path),
                                           "Size": self.get_file_size_by_file_path(file_path)}
                    file_path_map[file_path] = os.path.join(search_dir_web, possible_file.groups()[0])
                elif checked_file and camera_log_tag != None:
                    checked_file_path = os.path.join(search_dir_web, checked_file.groups()[0])
                    file_web[checked_file_path] = [file_mod_time, file_size]

        sorted_file = sorted(file_local.items(), key=operator.itemgetter(1))

        if camera_log_tag == None:
            if len(sorted_file) > 0:
                last_file_path = sorted_file[-1][0]
                remove_file_path = file_path_map[last_file_path]
                del file_web[remove_file_path]
            return file_web
        else:
            return file_web, file_info
