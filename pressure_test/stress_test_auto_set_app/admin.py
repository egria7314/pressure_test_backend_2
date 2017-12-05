from django.contrib import admin
from stress_test_auto_set_app.models import Email_server_private_parameter , Ftp_server_private_parameter , Nas_server_private_parameter

class Email_private_Admin(admin.ModelAdmin):
    list_display=('owner',) # for list diaplay by owner
    ordering=('owner',) #for sorting

class FTP_private_Admin(admin.ModelAdmin):
    list_display=('owner','test_type','location') # for list diaplay by owner
    ordering=('owner',) #for sorting

class NAS_private_Admin(admin.ModelAdmin):
    list_display=('owner','test_type','location') # for list diaplay by owner
    ordering=('owner',) #for sorting

admin.site.register(Email_server_private_parameter,Email_private_Admin)
admin.site.register(Ftp_server_private_parameter,FTP_private_Admin)
admin.site.register(Nas_server_private_parameter,NAS_private_Admin)
# Register your models here.
