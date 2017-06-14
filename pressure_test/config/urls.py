from django.conf.urls import url
# from pressure_test.camera_log import views
from rest_framework.urlpatterns import format_suffix_patterns
from config import views

# from website import views



urlpatterns = [
    url(r'^init_default', views.init_default_setting),
    url(r'^default/$', views.return_default_setting),
    url(r'^nas$', views.return_nas_location)
]

urlpatterns = format_suffix_patterns(urlpatterns)
