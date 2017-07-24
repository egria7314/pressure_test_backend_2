# -*- coding: utf-8 -*-
from django.urls import resolve
from django.test import Client
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.test import APITestCase
# from jarvis_commands.models import DqaIssue
# from jarvis_commands.models import UIPath
# from redmine_data.models import RedmineIssue, RedmineData
# from ddt import ddt, data, unpack



class BrokenTests(APITestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(username='testuser', password='12345', is_active=True, is_staff=True, is_superuser=True) 
        self.user.set_password('hello') 
        self.user.save() 
        self.user = authenticate(username='testuser', password='hello') 
        login = self.client.login(username='testuser', password='hello')

    def test_route_sync(self):
        """
        Ensure url routes path.
        """
        resolver = resolve('/pressure-tests/pretestbroken/')
        self.assertEqual(resolver.view_name, 'broken_tests.views.pretest_broken_image')

        resolver = resolve('/pressure-tests/projects/1/clips/')
        self.assertEqual(resolver.view_name, 'broken_tests.views.broken_report')

        resolver = resolve('/pressure-tests/projects/1/clips/1/')
        self.assertEqual(resolver.view_name, 'broken_tests.views.ClipInfoDetail')       

        resolver = resolve('/pressure-tests/projects/1/detectbroken/')
        self.assertEqual(resolver.view_name, 'broken_tests.views.detect_periodic_videos')

        resolver = resolve('/pressure-tests/projects/1/stopbroken/')
        self.assertEqual(resolver.view_name, 'broken_tests.views.stop_detect_periodic_videos')

        resolver = resolve('/pressure-tests/projects/1/statusbroken/')
        self.assertEqual(resolver.view_name, 'broken_tests.views.running_status')
