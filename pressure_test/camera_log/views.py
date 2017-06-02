from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated

# from pressure_test.camera_log.sd_status import SDstatus
from camera_log.sd_status import SDstatus
from camera_log.models import SdStatus
from camera_log.uptime import Uptime
from camera_log.models import UpTime


# Create your views here.

@api_view(['GET'])
@permission_classes((AllowAny,))
def get_sd_status(requests):
    camera_ip = "172.19.16.119"
    camera_user = "root"
    camera_pwd = "12345678z"

    my_sd_status = SDstatus(camera_ip, camera_user, camera_pwd)
    sd_status_json = my_sd_status.get_result()

    # my_up_time = Uptime(camera_ip, camera_user, camera_pwd)
    # my_up_time_json = my_up_time.get_result()



    SdStatus.objects.create(
        camera_ip=camera_ip,
        sd_status=sd_status_json["SD_status"],
        sd_used_percent=sd_status_json["SD_used_percent"],
    )

    # print(my_up_time)

    # UpTime.objects.create(
    #     camera_uptime=
    #
    # )
    #



    # data = requests.data
    # username = data.get('username')
    # password = data.get('password')
    #
    # try:
    #     # payload = {
    #     #     'username': username,
    #     #     'password': password
    #     # }
    #     # login_url = 'http://172.19.16.51:8881/jarvis-auth/auth_and_obtain_jwt_token'
    #     # r = req.post(login_url, data=payload)
    #     # print(r.text)
    #     # res_json = json.loads(r.text)
    #
    #     # requests.post( )
    # except Exception as e:
    #     print(e)

    return Response(sd_status_json)


@api_view(['GET'])
@permission_classes((AllowAny,))
def get_up_time(requests):
    camera_ip = "172.19.16.119"
    camera_user = "root"
    camera_pwd = "12345678z"

    my_up_time = Uptime(camera_ip, camera_user, camera_pwd)
    my_up_time_json = my_up_time.get_result()



    return Response(my_up_time_json)

