# -*- coding: utf-8 -*-
from django.test import TestCase
from config import views
from django.test import Client
from config.models import ProjectSetting


class Config(TestCase):

    def setUp(self):
        self.camera_ip = '172.19.16.156'
        self.camera_name = 'root'
        self.camera_password = '12345678z'

    def test_get_recording_prefix(self):
        prefix_name = views.get_recording_prefix(camera_ip=self.camera_ip, camera_name=self.camera_name,
                                                 camera_password=self.camera_password)
        self.assertEqual('unit_test_prefix', prefix_name)

    # def test_create_project_settings(self):
    #     import json
    #     client = Client()
    #     data = {"project_name": "test",
    #             "prefix_name":"",
    #             "start_time":"2017-06-13 07:56:59",
    #             "end_time":"2017-06-13 07:57:00",
    #             "owner": "steven",
    #             "ip":"172.19.16.156",
    #             "username":"root",
    #             "password":"12345678z",
    #             "type": "high",
    #             "path": "\\\\172.19.11.189\\Public\\autotest\\steven",
    #             "path_username": "autotest",
    #             "path_password": "autotest",
    #             "broken": "True",
    #             "continued": "False",
    #             "log": "False",
    #             "cgi":10,
    #             "delay":10}
    #     client.post('/save_project_setting/', json.dumps(data), content_type='application/json')
    #     query_set = ProjectSetting.objects.filter(project_name='test').values("id", "path", "project_name", "start_time", "log", "delay", "end_time",
    #                                                     "path_username", "continued", "username", "type", "broken", "owner",
    #                                                     "prefix_name", "cgi", "password", "path_password", "ip", "log_status", "broken_status",
    #                                                     "continuity_status")
    #     json = list(query_set)[0]
    #     self.assertEqual(json['project_name'], 'test')
    #     self.assertEqual(json['owner'], 'steven')
    #     self.assertEqual(json['ip'], '172.19.16.156')
    #     self.assertEqual(json['username'], 'root')
    #     self.assertEqual(json['password'], '12345678z')
    #     self.assertEqual(json['type'], 'high')
    #     self.assertEqual(json['path'], '//172.19.11.189/Public/autotest/steven')
    #     self.assertEqual(json['path_username'], 'autotest')
    #     self.assertEqual(json['path_password'], 'autotest')
    #     self.assertEqual(json['broken'], True)
    #     self.assertEqual(json['continued'], False)
    #     self.assertEqual(json['log'], False)
    #     self.assertEqual(json['cgi'], 10)
    #     self.assertEqual(json['delay'], 10)