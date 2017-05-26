from django.contrib import admin
from camera_log.models import SdStatus

class SdStatusAdmin(admin.ModelAdmin):
    list_display = ('sd_used_percent', 'sd_status', 'camera_ip')
    search_fields = ('sd_used_percent', 'sd_status', 'camera_ip')

admin.site.register(SdStatus, SdStatusAdmin)



