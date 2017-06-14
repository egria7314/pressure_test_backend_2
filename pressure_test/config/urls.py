from django.conf.urls import url
from config.lib import verify_script
# from pressure_test.camera_log import views
from rest_framework.urlpatterns import format_suffix_patterns
from config import views

# from website import views


urlpatterns = [
    url(r'^test_button/$', verify_script.test_button),
    # url(r'^mount/$', verify_script.mount_status),
    url(r'^pre_test/$', views.ProjectSettingList.as_view()),

    url(r'^pre_test/(?P<pk>[0-9]+)/$', views.ProjectSettingDetail.as_view()),
    url(r'^init_default', views.init_default_setting),
    url(r'^default/$', views.return_default_setting),
    url(r'^nas$', views.return_nas_location)
]

urlpatterns = format_suffix_patterns(urlpatterns)
