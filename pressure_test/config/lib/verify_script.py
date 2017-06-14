from django.http import HttpResponse
import subprocess
import time
import os


def test_button(request):
    test_info = request.GET["info"]
    test_info = test_info.split(' ')
    ip = test_info[0]
    destination = test_info[1]
    username = test_info[2]
    password = test_info[3]
    ping_result = ping_camera(ip)
    mount_result = mount_status(destination, username, password)

    return HttpResponse("{0}, {1}".format(ping_result, mount_result))

def ping_camera(ip):
    # ip = request.GET["ip"]
    print('ip:', ip)
    ping_result = ''
    for i in range(3):
        ping_result = __ping_test(ip=ip)
        print('print result: ', ping_result)
        if ping_result == 'Connection successful':
            break
        time.sleep(10)

    if ping_result != 'Connection successful':
        raise Exception('FW_UI Automation can not ping camera.')

    return ping_result

def __ping_test(ip):
    try:
        ping = subprocess.Popen(["ping", "-c", "3", ip], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, error = ping.communicate()
        print('out:', out)
        if out:
            if 'ttl' in str(out):
                return 'Connection successful'
            else:
                return 'Connection failed'
        else:
            return 'No ping'
    except subprocess.CalledProcessError:
        return "Couldn't get a ping"

def mount_status(destination, username, password):
    # storage_info = request.GET["info"]
    # storage_info = storage_info.split(' ')
    source = '/home/dqa/data/mnt'
    if not os.path.exists(source):
        os.makedirs(source)
        os.chmod(source, 0o777)
    # destination = '//172.19.13.3/dqa03_backup/gitlab'
    # destination = storage_info[0]
    # username = 'admin'
    # username = storage_info[1]
    # password = '490520755'
    # password = storage_info[2]
    check_status = subprocess.Popen(["df"], stdout=subprocess.PIPE)
    out, error = check_status.communicate()
    mount_result = ''
    if out:
        if destination not in str(out):
            subprocess.Popen("sudo mount -t cifs {0} {1} -o username={2},password={3}".format(destination, source, username, password), shell=True)
            status = subprocess.Popen(["df"], stdout=subprocess.PIPE)
            out, error = status.communicate()
            if out:
                if destination in str(out):
                    mount_result = 'Mount storage successful'
                else:
                    mount_result = 'Mount storage failed'
        else:
            mount_result = "Mount storage exist"
    return mount_result