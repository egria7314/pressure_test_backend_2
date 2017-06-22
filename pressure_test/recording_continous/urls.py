from django.conf.urls import url
# from pressure_test.camera_log import views
from rest_framework.urlpatterns import format_suffix_patterns
from recording_continous import views

# from website import views



urlpatterns = [
    url(r'^implement_in/$', views.implement_in),
    url(r'^ana_videos/(?P<project_id>[0-9]+)/$', views.ana_videos),
    url(r'^continous_report/(?P<project_id>[0-9]+)/$', views.continuous_report),


]

urlpatterns = format_suffix_patterns(urlpatterns)
