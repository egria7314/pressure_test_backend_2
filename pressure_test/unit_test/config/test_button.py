# -*- coding: utf-8 -*-
from django.test import TestCase
from config.helpers import verify_script


class TestButton(TestCase):

    def test_ping_camera_success(self):
        camera_ip = '172.19.16.156'
        ping_result = verify_script.ping_camera(ip=camera_ip)
        self.assertEqual('Camera connection successful', ping_result)

    def test_ping_camera_fail(self):
        camera_ip = '172.18.16.119'
        ping_result = verify_script.ping_camera(ip=camera_ip)
        self.assertEqual('Can not ping camera', ping_result)

    def test_mount_nas_success(self):
        nas_destination = '//192.168.14.6/gitlab'
        nas_username = ''
        nas_password = ''
        mount_result = verify_script.mount_status(destination=nas_destination, username=nas_username, password=nas_password)
        self.assertEqual('Mount storage successful', mount_result)

    def test_mount_nas_fail(self):
        nas_destination = '//192.168.14.5/gitlab'
        nas_username = ''
        nas_password = ''
        mount_result = verify_script.mount_status(destination=nas_destination, username=nas_username, password=nas_password)
        self.assertEqual('Mount storage failed', mount_result)

    def test_button(self):
        verify_script.test_button()
