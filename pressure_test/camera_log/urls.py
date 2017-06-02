from django.conf.urls import url
# from pressure_test.camera_log import views
from rest_framework.urlpatterns import format_suffix_patterns
from camera_log import views

# from website import views



urlpatterns = [
    url(r'^sd_status/$', views.get_sd_status),
    url(r'^up_time/$', views.get_up_time),
]

urlpatterns = format_suffix_patterns(urlpatterns)
