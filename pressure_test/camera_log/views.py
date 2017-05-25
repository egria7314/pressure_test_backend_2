from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated

# from pressure_test.camera_log.sd_status import SDstatus
from camera_log.sd_status import SDstatus



# Create your views here.

@api_view(['GET'])
@permission_classes((AllowAny,))
def get_sd_status(requests):
    camera_ip = "172.19.16.119"
    camera_user = "root"
    camera_pwd = "12345678z"

    NasStorage = SDstatus(camera_ip, camera_user, camera_pwd)
    res_json = NasStorage.get_result()

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

    return Response(res_json)
    # return Response('abc')




#
#
# from django.http import HttpResponse
# from django.shortcuts import render_to_response
# from rest_framework.response import Response
# from rest_framework import generics
# from rest_framework import permissions
# from rest_framework.decorators import api_view, permission_classes
# from rest_framework import permissions
# import requests as req
# import json
#
# # JARVIS_IP =
#
#
# # Create your views here.
# @api_view(['GET'])
# def index_view(requests):
#     return render_to_response('index.html')
#
#
# @api_view(['GET'])
# def dashboard_view(requests):
#
#     return render_to_response('dashboard.html')
#
#
# @api_view(['GET'])
# def loginpage_view(requests):
#     return render_to_response('loginpage.html')
#
#
# @api_view(['POST'])
# @permission_classes((permissions.AllowAny,))
# def parse_login_info(requests):
#     data = requests.data
#     username = data.get('username')
#     password = data.get('password')
#
#     try:
#         payload = {
#             'username': username,
#             'password': password
#         }
#         login_url = 'http://172.19.16.51:8881/jarvis-auth/auth_and_obtain_jwt_token'
#         r = req.post(login_url, data=payload)
#         print(r.text)
#         res_json = json.loads(r.text)
#
#         # requests.post( )
#     except Exception as e:
#         print(e)
#
#     return Response(res_json)
#     # return Response('abc')
