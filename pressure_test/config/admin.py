# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from config.models import ProjectSetting
from config.models import DefaultSetting
from django.contrib import admin

# Register your models here.
class ProjectSettingAdmin(admin.ModelAdmin):
    list_display = ('id', 'project_name', 'prefix_name', 'start_time', 'end_time', 'owner', 'ip', 'username', 'password', 'type', 'path', 'path_username',
                    'path_password', 'broken', 'continued', 'log', 'cgi', 'delay')

class DefaultSettingAdmin(admin.ModelAdmin):
    list_display = ('default_type', 'log_sd_card_status', 'log_cyclic_recording', 'log_nas_recording', 'broken_image',
                    'cont_inner_serial_timstamp', 'cont_outer_serial_timstamp', 'cgi', 'delay')

admin.site.register(ProjectSetting, ProjectSettingAdmin)
admin.site.register(DefaultSetting, DefaultSettingAdmin)