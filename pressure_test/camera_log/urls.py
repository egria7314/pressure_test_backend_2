from django.conf.urls import url
# from pressure_test.camera_log import views
from rest_framework.urlpatterns import format_suffix_patterns
from camera_log import views

# from website import views



urlpatterns = [
    url(r'^sd_status/$', views.get_sd_status),
]

# urlpatterns = [
#     url(r'^$', views.dashboard_view),
#     url(r'^dashboard/$', views.dashboard_view),
#     url(r'^login/$', views.loginpage_view),
#     url(r'^parse_login_info/$', views.parse_login_info)
# ]

urlpatterns = format_suffix_patterns(urlpatterns)
