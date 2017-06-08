# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

class ProjectSetting(models.Model):
    project_name = models.CharField(max_length=100)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    owner = models.CharField(max_length=100)
    ip = models.CharField(max_length=100)
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)

    CHOICES = (
        ('MED', 'Medium'),
        ('HIGH', 'High')
    )
    type = models.CharField(max_length=100, choices=CHOICES, default='MED')
    path = models.CharField(max_length=100)
    path_username = models.CharField(max_length=100)
    path_password = models.CharField(max_length=100)
    broken = models.BooleanField(default=False)
    continued = models.BooleanField(default=False)
    log = models.BooleanField(default=False)
    cgi = models.TimeField()
    delay = models.TimeField()
