"""pressure_test URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from stress_test_auto_set_app.views import stress_test


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^', include('camera_log.urls')),
    url(r'^', include('config.urls')),
    url(r'^', include('recording_continous.urls')),
    url(r'^', include('broken_tests.urls')),
    url(r'^', include('version.urls')),
    url(r'^stress_test/$',stress_test),
    url(r'^stress_test/\
        camera_ip=\d{1,3}[.]\d{1,3}[.]\d{1,3}[.]\d{1,3}&camera_account=\w{1,64}&camera_password=\w{1,64}&tester=\w{1,10}&test_type=\w{1,15}&camera_type=\w{1,10}&test_location=\w{1,6}&submit=yes/$',stress_test),

]