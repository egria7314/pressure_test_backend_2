from django.contrib import admin
from broken_tests.models import CameraProfile, NasProfile, ClipInfo, BrokenFrame

# Register your models here.
class CameraProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'host', 'user', 'password', 'get_project_profile_id', )
    search_fields = ('host', 'user', 'password', )

class NasProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'password', 'location', 'workgroup', 'get_project_profile_id', )
    search_fields = ('user', 'password', 'location', 'workgroup', )

class ClipInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'path', 'privacy_masks', 'is_broken', )
    search_fields = ('path', 'privacy_masks', 'is_broken', )

class BrokenFrameAdmin(admin.ModelAdmin):
    list_display = ('id', 'error_message', 'frame_path', 'timestamp', )
    search_fields = ('error_message', 'frame_path', 'timestamp', )

admin.autodiscover()
admin.site.register(CameraProfile, CameraProfileAdmin)
admin.site.register(NasProfile, NasProfileAdmin)
admin.site.register(ClipInfo, ClipInfoAdmin)
admin.site.register(BrokenFrame, BrokenFrameAdmin)