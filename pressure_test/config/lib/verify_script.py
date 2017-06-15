from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
import subprocess
import time
import os


@api_view(['GET'])
def test_button(request):
    ip = request.GET["ip"]
    path = request.GET["path"]
    username = request.GET["path_username"]
    password = request.GET["path_password"]
    ping_result = ping_camera(ip)
    mount_result = mount_status(path, username, password)
    test_result = {}
    if ping_result == 'Connection successful' and (mount_result == 'Mount storage successful' or mount_result == "Mount storage exist"):
        test_result = {"testCheck": True, "info": {"action": "pretest", "status": "success", "comment": "{0}, {1}".format(ping_result, mount_result)}}
    elif ping_result != 'Connection successful' or mount_result != 'Mount storage successful':
        test_result = {"testCheck": False, "info": {"action": "pretest", "status": "failed", "comment": "{0}, {1}".format(ping_result, mount_result)}}
    # elif mount_result != 'Mount storage successful':
    #     test_result = {"testCheck": False, "info": {"action": "pretest", "status": "failed", "comment": "{0}".format(mount_result)}}

    return Response(test_result)

def ping_camera(ip):
    print('ip:', ip)
    ping_result = ''
    for i in range(3):
        ping_result = __ping_test(ip=ip)
        print('print result: ', ping_result)
        if ping_result == 'Connection successful':
            break
        time.sleep(10)

    if ping_result != 'Connection successful':
        raise Exception('Can not ping camera')

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
    source = '/home/dqa/data/mnt'
    if not os.path.exists(source):
        os.makedirs(source)
        os.chmod(source, 0o777)
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