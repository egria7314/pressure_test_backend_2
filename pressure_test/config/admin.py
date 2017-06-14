# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from config.models import ProjectSetting
from django.contrib import admin

# Register your models here.
class ProjectSettingAdmin(admin.ModelAdmin):
    list_display = ('project_name', 'prefix_name', 'start_time', 'end_time', 'owner', 'ip', 'username', 'password', 'type', 'path', 'path_username',
                    'path_password', 'broken', 'continued', 'log', 'cgi', 'delay')


admin.site.register(ProjectSetting, ProjectSettingAdmin)