# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from stress_test_auto_set_app.common_action import Stress_auto_set


def stress_test(request):
    if 'submit' in request.GET:
        stress=Stress_auto_set()
        host, tester, test_type, camera_type, location = stress.get_section_data(request)
        stress.set_email_server(host , tester)
        stress.set_ftp_server(host , tester , test_type , location)
        stress.set_nas_server(host, tester, test_type, location)
        stress.set_privacy_mask(host,camera_type)
        stress.set_motion_window(host,test_type)
        stress.set_media(host)
        stress.set_reboot_event(host)
        stress.set_motion_event(host)
        stress.set_preiodically_event(host,test_type)
        stress.set_recording_sd(host,test_type)
        if test_type == 'Stress_Test':
            stress.set_recording_nas(host)
        result_message = 'finish set up ! please check camera'
    return render_to_response('stress_test.html',locals())

# Create your views here.
