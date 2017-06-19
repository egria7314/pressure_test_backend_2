from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
import subprocess
import time
import os
import urllib.request
import json
import ast
import requests


@api_view(['GET'])
def test_button(request):
    ip = request.GET["ip"]
    username = request.GET["username"]
    password = request.GET["password"]
    path = request.GET["path"]
    path_username = request.GET["path_username"]
    path_password = request.GET["path_password"]
    broken = request.GET["broken"]
    # print(type(broken))
    test_broken_result = ""
    test_broken_error = ""
    url = 'http://172.19.16.51:8000/pressure-tests/pretestbroken?host={0}&user={1}&password={2}'.format(ip, username, password)
    if broken == 'true':
        response = requests.get(url)
        print(response.json())
        broken_result = response.json()
        print("broken_result:", broken_result)
        if broken_result['results'] == "passed":
            test_broken_result = "Test broken successful"
            test_broken_error = "OK"
        else:
            test_broken_result = "Test broken failed"
            test_broken_error = broken_result["error_boxes"]

    ping_result = ping_camera(ip)
    mount_result = mount_status(path, path_username, path_password)
    test_result = {}
    if ping_result == 'Camera connection successful' and (mount_result == 'Mount storage successful' or mount_result == "Mount storage exist"):
        test_result = {"testCheck": True, "info": {"action": "pretest", "status": "success", "comment": "{0}, {1}, {2}: {3}".format(ping_result, mount_result, test_broken_result, test_broken_error)}}
    elif ping_result != 'Camera connection successful' or mount_result != 'Mount storage successful':
        test_result = {"testCheck": False, "info": {"action": "pretest", "status": "failed", "comment": "{0}, {1}, {2}: {3}".format(ping_result, mount_result, test_broken_result, test_broken_error)}}

    return Response(test_result)

def ping_camera(ip):
    # print('ip:', ip)
    ping_result = ''
    for i in range(3):
        ping_result = __ping_test(ip=ip)
        # print('print result: ', ping_result)
        if ping_result == 'Camera connection successful':
            break
        time.sleep(10)

    if ping_result != 'Camera connection successful':
        raise Exception('Can not ping camera')

    return ping_result

def __ping_test(ip):
    try:
        ping = subprocess.Popen(["ping", "-c", "3", ip], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, error = ping.communicate()
        # print('out:', out)
        if out:
            if 'ttl' in str(out):
                return 'Camera connection successful'
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