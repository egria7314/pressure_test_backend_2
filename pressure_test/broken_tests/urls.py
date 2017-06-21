from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from broken_tests import views
from broken_tests import signals 


urlpatterns = [
	url(r'^pressure-tests/projects/(?P<project_pk>[0-9]+)/clips/$', views.broken_report),
	url(r'^pressure-tests/projects/(?P<project_pk>[0-9]+)/clips/(?P<clip_pk>[0-9]+)/$', views.ClipInfoDetail.as_view()),
    url(r'^pressure-tests/projects/(?P<project_pk>[0-9]+)/detectbroken/$', views.detect_periodic_videos),
	url(r'^pressure-tests/projects/(?P<project_pk>[0-9]+)/stopbroken/$', views.stop_detect_periodic_videos),
	url(r'^pressure-tests/projects/(?P<project_pk>[0-9]+)/statusbroken/$', views.running_status),
    url(r'^pressure-tests/pretestbroken/$', views.pretest_broken_image),

    # [TODO] next features, with compatibility
	# url(r'^pressure-tests/brokenframes/$', views.BrokenFrameList.as_view()),
	# url(r'^pressure-tests/borkenframes/(?P<pk>[0-9]+)/$', views.BrokenFrameDetail.as_view()),

]

urlpatterns = format_suffix_patterns(urlpatterns)
