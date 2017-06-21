from django.contrib import admin
from recording_continous.models import RecordingContinuty
from recording_continous.models import RecordingFile
from recording_continous.models import Config

class RecordingContinutyAdmin(admin.ModelAdmin):
    list_display = ('project_id', 'creat_at', 'video_path', 'video_path_before', 'size','in_result','error_code',"start_time" , "end_time", 'link','count', 'between_result', 'seconds')
    search_fields = ('project_id', 'creat_at', 'video_path', 'video_path_before','size','in_result','error_code',"start_time" , "end_time", 'link','count', 'between_result', 'seconds')


class RecordingFileAdmin(admin.ModelAdmin):
    list_display = ('project_id', 'modify_time', 'size', 'path', 'status')
    search_fields = ('project_id', 'modify_time', 'size', 'path', 'status')

class ConfigAdmin(admin.ModelAdmin):
    list_display = ('project_id', 'start_time', 'end_time', 'delay_time')
    search_fields = ('project_id', 'start_time', 'end_time', 'delay_time')



admin.site.register(RecordingContinuty, RecordingContinutyAdmin)
admin.site.register(RecordingFile, RecordingFileAdmin)
admin.site.register(Config, ConfigAdmin)



