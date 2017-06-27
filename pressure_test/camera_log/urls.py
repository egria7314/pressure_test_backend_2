from django.conf.urls import url
# from pressure_test.camera_log import views
from rest_framework.urlpatterns import format_suffix_patterns
from camera_log import views

# from website import views



urlpatterns = [
    url(r'^sd_status/$', views.get_sd_status),
    url(r'^up_time/$', views.get_up_time),
    url(r'^epoch_time/$', views.get_epoch_time),
    url(r'^sd_recording_file/$', views.get_sd_recording_file),
    url(r'^camera_log/$', views.test_set_camera_api),
    # url(r'^camera_log/$', views.run_camera_schedule),
    url(r'^test_camera_log/$', views.test_camera),

    url(r'^get_camera_log_schedule/$', views.get_schedule_status),

    url(r'^stop_camera_log_schedule/$', views.test_stop_camera_logs),
    url(r'^camera_log_status/$', views.test_camera_status),


    url(r'^logs/(?P<pi>[0-9]+)/$', views.get_all_camera_log)
]

urlpatterns = format_suffix_patterns(urlpatterns)
