from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from version import views

urlpatterns = [
    url(r'^version/$', views.get_version),
]

urlpatterns = format_suffix_patterns(urlpatterns)
