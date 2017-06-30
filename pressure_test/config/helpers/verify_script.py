from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from broken_tests.views import module_pretest_broken_image
import subprocess
import time
import os


@api_view(['GET'])
def test_button(request):
    project_name = request.GET["project_name"]
    start_time = request.GET["start_time"]
    end_time = request.GET["end_time"]
    owner = request.GET["owner"]
    cgi = request.GET["cgi"]
    delay = request.GET["delay"]
    ip = request.GET["ip"]
    username = request.GET["username"]
    password = request.GET["password"]
    path = request.GET["path"]
    path_username = request.GET["path_username"]
    path_password = request.GET["path_password"]
    broken = request.GET["broken"]
    type = request.GET["type"]

    field_dict = {"project_name":project_name, "start_time":start_time, "end_time":end_time, "owner":owner, "cgi":cgi, "delay":delay,
                  "ip":ip, "username":username, "password":password, "path":path, "path_username":path_username, "path_password":path_password}
    error_string, input_field = [], "Pass"
    for key, value in field_dict.items():
        if value == "":
            error_string.append(key)
    if error_string:
        input_field = "{0} field may not be blank".format(', '.join(error_string))
    ping_result = ping_camera(ip)
    mount_result = mount_status(path, path_username, path_password)
    if broken == 'true':
        test_broken_result = module_pretest_broken_image(camera_host=ip, camera_user=username, camera_password=password, storage_type=type)
        test_result = get_result(ping_result=ping_result, mount_result=mount_result, test_broken_result=test_broken_result, error_string=error_string, input_field=input_field)
    else:
        test_result = get_result(ping_result=ping_result, mount_result=mount_result, input_field=input_field, error_string=error_string)

    return Response(test_result)

def get_result(ping_result, mount_result, error_string, input_field, test_broken_result=None):
    if type(test_broken_result) == dict:
        if ping_result == 'Camera connection successful' and (mount_result == 'Mount storage successful' or mount_result == "Mount storage already exist") and error_string == [] and test_broken_result['result'] == "passed":
            test_result = {
                "testCheck": True, "info": {
                    "action": "pretest", "status": "success", "comment": "{0}, {1}, Broken test: {2}".format(ping_result, mount_result, test_broken_result)
                }
            }
        else:
            test_result = {
                "testCheck": False, "info": {
                    "action": "pretest", "status": "failed", "comment": "{0}, {1}, Broken test: {2}, Field check: {3}".format(ping_result, mount_result, test_broken_result, input_field)
                }
            }
    else:
        if ping_result == 'Camera connection successful' and (mount_result == 'Mount storage successful' or mount_result == "Mount storage already exist") and error_string == []:
            test_result = {
                "testCheck": True, "info": {
                    "action": "pretest", "status": "success", "comment": "{0}, {1}".format(ping_result, mount_result)
                }
            }
        else:
            test_result = {
                "testCheck": False, "info": {
                    "action": "pretest", "status": "failed", "comment": "{0}, {1}, Field check: {2}".format(ping_result, mount_result, input_field)
                }
            }
    return test_result

# def get_result(ping_result, mount_result, input_field, error_string):
#     if ping_result == 'Camera connection successful' and (mount_result == 'Mount storage successful' or mount_result == "Mount storage already exist") and error_string == []:
#             test_result = {
#                 "testCheck": True, "info": {
#                     "action": "pretest", "status": "success", "comment": "{0}, {1}".format(ping_result, mount_result)
#                 }
#             }
#     else:
#         test_result = {
#             "testCheck": False, "info": {
#                 "action": "pretest", "status": "failed", "comment": "{0}, {1}, Field check: {2}".format(ping_result, mount_result, input_field)
#             }
#         }
#     return test_result

def ping_camera(ip):
    ping_result = ''
    for i in range(3):
        ping_result = __ping_test(ip=ip)
        if ping_result == 'Camera connection successful':
            break
        time.sleep(10)

    if ping_result != 'Camera connection successful':
        ping_result = 'Can not ping camera'
        # raise Exception('Can not ping camera')

    return ping_result

def __ping_test(ip):
    try:
        ping = subprocess.Popen(["ping", "-c", "3", ip], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, error = ping.communicate()
        if out:
            if 'ttl' in str(out):
                return 'Camera connection successful'
            else:
                return 'Camera Connection failed'
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
    if destination:
        if out:
            # print(os.path.join(destination, '').replace('\\', '/'))
            if os.path.join(destination, '').replace('\\', '/') not in str(out):
                subprocess.Popen("sudo mount -t cifs {0} {1} -o username={2},password={3}".format(os.path.join(destination, '').replace('\\', '/'), source, username, password), shell=True)
                time.sleep(3)
                status = subprocess.Popen(["df"], stdout=subprocess.PIPE)
                out, error = status.communicate()
                if out:
                    if destination.replace('\\', '/') in str(out):
                        mount_result = 'Mount storage successful'
                    else:
                        mount_result = 'Mount storage failed'
            else:
                mount_result = "Mount storage already exist"
    else:
        mount_result = 'Mount storage failed'
    return mount_result