# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from rest_framework.response import Response
from config.serializers import ProjectSettingSerializer
from rest_framework import generics
from config.models import ProjectSetting
from rest_framework import serializers


class ProjectSettingDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProjectSetting.objects.all()
    serializer_class = ProjectSettingSerializer

class ProjectSettingList(generics.ListCreateAPIView):
    queryset = ProjectSetting.objects.all()
    serializer_class = ProjectSettingSerializer
