# -*- coding: utf-8 -*-
"""This module implement for using cgi to get or set the parameter of camera.

.. module:: common_cgi.
        :synopsis: A module for using cgi to get or set the parameter of camera

.. moduleauthor:: fw_ui_team

"""

import base64
import urllib.request, urllib.error, urllib.parse
# import time
import re
# from urllib.error import HTTPError


class CGI():
    """using cgi to get or set the parameter of camera"""
    def get_cgi(self, username, password, host, cgi_command, cgi_type='getparam.cgi'):
        """using cgi to get the parameter of camera
        Args:
            username (str): Camera user name
            password (str): Camera user password
            host (str): camera host address
            cgi_command (str): parameter name
            cgi_type (str): cgi type, default is getparam.cgi
        Returns:
            str
        ::
            str -- ex: system_info_modelname='CC8160'
        """
        if password != '':
            auth_str = username + ":" + password
            auth_str = auth_str.replace('\n', '')
            auth_byte_str = auth_str.encode(encoding="utf-8")
            encode_str = base64.b64encode(auth_byte_str)

        else:
            encode_str = ''

        req = urllib.request.Request('http://' + host + '/cgi-bin/admin/{0}?'.format(cgi_type) + cgi_command)
        req.add_header("Authorization", "Basic " + encode_str.decode())
        response = urllib.request.urlopen(req)
        cgi = re.split(b"\\r\\n", response.read())

        return cgi[0].decode("utf-8")

#
#
#     def check_set_cgi_success(self, con, cgi_command, cgi_type, response_code):
#         if cgi_type=='setparam.cgi?':
#             return con == cgi_command.replace('&', '')
#         else:
#             return response_code == 200
#
#     def set_cgi(self, username, password, host, cgi_command, cgi_type='setparam.cgi?', back_door='0'):
#         """using cgi to set the parameter of camera
#         Args:
#             username (str): Camera user name
#             password (str): Camera user password
#             host (str): camera host address
#             cgi_command (str): parameter name and value
#         Returns:
#             none.
#
#         """
#         # time.sleep(1)
#         if password != '':
#             base64string = base64.encodestring('%s:%s' \
#                                                % (username, password)).replace('\n', '')
#         else:
#             base64string = ''
#         req = urllib.request.Request('http://' + host + '/cgi-bin/admin/' + cgi_type + cgi_command)
#         req.add_header("Authorization", "Basic " + base64string)
#         count = 0
#         con, response, response_code, response_text = '', '', 999, '' # 999 by default
#
#         while count < 5 and not self.check_set_cgi_success(con, cgi_command, cgi_type, response_code):
#             try:
#                 response = urllib.request.urlopen(req)
#                 con = re.sub("\\r\\n", '', response.read())
#                 con = re.sub("'", '', con)
#                 con = re.sub(r"\\\\", r"\\", con)
#                 response_code = response.getcode()
#                 count += 1
#                 if back_door == '1':
#                     break
#                 time.sleep(1)
#             except HTTPError:
#                 count += 1
#                 time.sleep(5)
#
#         set_cgi = cgi_type + cgi_command
#         if count >=5:
#             return 'Http Error: {0} '.format(set_cgi)
#         else:
#             return 'Http Status-{0}: {1}'.format(response.getcode(), set_cgi), con
#


# # sd_support_cgi_result = CGI().get_cgi("root", "12345678z", "172.19.16.119", "capability_supportsd")    # sd support
# sd_support_cgi_result = CGI().get_cgi("root", "12345678z", "172.19.1.39", "capability_supportsd")    # sd not support
#
# print(sd_support_cgi_result)
#
# m = re.match(r"(.*)=\'(.*)\'", sd_support_cgi_result)
# print(m.group(2))