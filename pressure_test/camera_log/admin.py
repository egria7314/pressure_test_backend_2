from django.contrib import admin
from camera_log.models import SdStatus
from camera_log.models import UpTime

class SdStatusAdmin(admin.ModelAdmin):
    list_display = ('sd_used_percent', 'sd_status', 'camera_ip')
    search_fields = ('sd_used_percent', 'sd_status', 'camera_ip')


class UpTimeAdmin(admin.ModelAdmin):
    list_display = ('camera_uptime', 'camera_cpuloading_average', 'camera_cpuloading_idle')
    search_fields = ('camera_uptime', 'camera_cpuloading_average', 'camera_cpuloading_idle')


admin.site.register(SdStatus, SdStatusAdmin)
admin.site.register(UpTime, UpTimeAdmin)



