from django.contrib import admin
from camera_log.models import SdStatus
from camera_log.models import UpTime
from camera_log.models import EpochTime
from camera_log.models import SdRecordingFile


class SdStatusAdmin(admin.ModelAdmin):
    list_display = ('sd_used_percent', 'sd_status', 'camera_ip')
    search_fields = ('sd_used_percent', 'sd_status', 'camera_ip')

class UpTimeAdmin(admin.ModelAdmin):
    list_display = ('camera_uptime', 'camera_cpuloading_average', 'camera_cpuloading_idle')
    search_fields = ('camera_uptime', 'camera_cpuloading_average', 'camera_cpuloading_idle')

class EpochTimeAdmin(admin.ModelAdmin):
    list_display = ('camera_epoch_time',)
    search_fields = ('camera_epoch_time',)

class SdRecordingFileAdmin(admin.ModelAdmin):
    list_display = ('locked_file', 'unlocked_file', 'all_file')
    search_fields = ('locked_file', 'unlocked_file', 'all_file')

    #
    # locked_file = models.CharField(null=True, blank=True, max_length=100)
    # unlocked_file = models.CharField(null=True, blank=True, max_length=100)
    # all_file = models.CharField(null=True, blank=True, max_length=100)



admin.site.register(SdStatus, SdStatusAdmin)
admin.site.register(UpTime, UpTimeAdmin)
admin.site.register(EpochTime, EpochTimeAdmin)
admin.site.register(SdRecordingFile, SdRecordingFileAdmin)



