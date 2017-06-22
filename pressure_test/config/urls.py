from django.conf.urls import url
from config.helpers import verify_script
# from pressure_test.camera_log import views
from rest_framework.urlpatterns import format_suffix_patterns
from config import views
from config.helpers import monitor

# from website import views


urlpatterns = [
    url(r'^test_button/$', verify_script.test_button),
    url(r'^init_default', views.init_default_setting),
    url(r'^default/$', views.return_default_setting),
    url(r'^nas$', views.return_nas_location),
    url(r'^projects/(?P<pk>[0-9]+)/$', views.return_project_setting),
    url(r'^projects/$', views.return_project_setting),
    url(r'^save_project_setting/$', views.post),
    url(r'^monitor_alive/$', monitor.monitor_alive),
    url(r'^daily-summary/(?P<pk>[0-9]+)/$', views.return_daily_summary)
]

urlpatterns = format_suffix_patterns(urlpatterns)
