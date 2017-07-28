# -*- coding: utf-8 -*-
from django.test import TestCase
from config.helpers import verify_script
from django.test import Client


class TestButton(TestCase):

    def setUp(self):
        self.client = Client()

    def test_ping_camera_success(self):
        camera_ip = '172.19.16.156'
        ping_result = verify_script.ping_camera(ip=camera_ip)
        self.assertEqual('Camera connection successful', ping_result)

    def test_ping_camera_fail(self):
        camera_ip = '172.18.16.156'
        ping_result = verify_script.ping_camera(ip=camera_ip)
        self.assertEqual('Can not ping camera', ping_result)

    def test_mount_nas_success(self):
        nas_destination = '//192.168.14.6/gitlab'
        nas_username = ''
        nas_password = ''
        mount_result = verify_script.mount_status(destination=nas_destination, username=nas_username,
                                                  password=nas_password)
        self.assertEqual('Mount storage successful', mount_result)

    def test_mount_nas_fail(self):
        nas_destination = '//192.168.14.5/gitlab'
        nas_username = ''
        nas_password = ''
        mount_result = verify_script.mount_status(destination=nas_destination, username=nas_username,
                                                  password=nas_password)
        self.assertEqual('Mount storage failed', mount_result)

    def test_button(self):
        resp = self.client.get('/test_button/?project_name=project_test&'
                               'start_time=Tue%20Jun%2020%202017%2010%3A00%3A23%20GMT%2B0800%20(CST)&'
                               'end_time=Tue%20Jun%2020%202017%2010%3A00%3A23%20GMT%2B0800%20(CST)&'
                               'owner=leo&'
                               'ip=172.19.16.119&'
                               'username=root&'
                               'password=12345678z&'
                               'type=medium&'
                               'path=//172.19.13.3/dqa03_backup/gitlab&'
                               'path_username=admin&'
                               'path_password=490520755&'
                               'broken=true&'
                               'continued=false&'
                               'log=true&'
                               'cgi=10&'
                               'delay=10')

        self.assertEqual(resp.status_code, 200)