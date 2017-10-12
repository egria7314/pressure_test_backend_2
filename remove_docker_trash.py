from subprocess import Popen, PIPE
import datetime
import os
import time

target_list = ['/var/lib/docker/aufs/diff/', '/var/lib/docker/aufs/mnt/']
while True:

    # cmd = 'sudo -S rm -rf /var/lib/docker/aufs/diff/f3e29b9cac6cee353a42efe6bd970b3db51a557eae65976b2c42a663686fdec3/'
    # os.system('echo 123 | {0}'.format(cmd))
    for path in target_list:
        get_file_list ='cd {0} && ls'.format(path)

        p = Popen([get_file_list], stdout=PIPE, stderr=PIPE, stdin=PIPE, shell=True)
        stdout, stderr = p.communicate()
        # print (stdout)
        dirs = stdout.split('\n')
        print ("Current time:{0}".format(datetime.datetime.now()))
        now = datetime.datetime.now()
        for d in dirs:
            p = '{0}{1}'.format(path, d)
            timestamp = os.path.getctime(p)
            date = datetime.datetime.fromtimestamp(timestamp)
            date_str = date.strftime('%Y-%m-%d %H:%M:%S')
            if now-date> datetime.timedelta(days=15):
                cmd = 'sudo -S rm -rf {0}{1}/'.format(path, d)
                os.system('{0}'.format(cmd))
                print ("Delete:{0}   {1}".format(d,date_str))
        print("Finish delete trash in {0}".format(path))
    print ("Time to sleep!")
    time.sleep(86400)

