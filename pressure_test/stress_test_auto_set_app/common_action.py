from stress_test_auto_set_app.models import Email_server_private_parameter, Ftp_server_private_parameter,Nas_server_private_parameter
import urllib
import base64
import re

class Stress_auto_set:
    def get_cgi(self, host, cgi_parameter, timeout=10):

        if not self.camera_passwd == '':
            auth_str = self.camera_account + ":" + self.camera_passwd
            auth_str = auth_str.replace('\n', '')
            auth_byte_str = auth_str.encode(encoding="utf-8")
            encode_str = base64.b64encode(auth_byte_str)
        else:
            encode_str = ''
        request = urllib.request.Request('http://' + host + '/cgi-bin/admin/getparam.cgi?' + cgi_parameter)
        request.add_header("Authorization", "Basic " + encode_str.decode())
        response = urllib.request.urlopen(request, timeout=timeout)
        cgi_response = re.split(b"\\r\\n", response.read())
        print(cgi_response)
        return cgi_response[0].decode("utf-8")


    def set_cgi(self, host, cgi_parameter, value='',timeout=30):

        if not self.camera_passwd == '':
            auth_str = self.camera_account + ":" + self.camera_passwd
            auth_str = auth_str.replace('\n', '')
            auth_byte_str = auth_str.encode(encoding="utf-8")
            encode_str = base64.b64encode(auth_byte_str)
        else:
            encode_str = ''

        if value =='':
            url = "http://" + str(host) + "/cgi-bin/admin/setparam.cgi"
            data = urllib.parse.urlencode(cgi_parameter)

            request = urllib.request.Request(url, data.encode())
        else:
            url = "http://" + str(host) + "/cgi-bin/admin/setparam.cgi?" + str(cgi_parameter) + "=" + str(value)
            request = urllib.request.Request(url)


        request.add_header("Authorization", "Basic " + encode_str.decode())
        response = urllib.request.urlopen(request, timeout=timeout)
        cgi_response = response.read()
        cgi = re.split(b"\\r\\n", response.read())
        print(cgi_response)
        return cgi[0].decode("utf-8")



    def set_cgi_camctrl(self, host, cgi_parameter, value='',timeout=30):

        '''for /cgi-bin/camctrl/camctrl.cgi? use'''
        if not self.camera_passwd == '':
            auth_str = self.camera_account + ":" + self.camera_passwd
            auth_str = auth_str.replace('\n', '')
            auth_byte_str = auth_str.encode(encoding="utf-8")
            encode_str = base64.b64encode(auth_byte_str)
        else:
            encode_str = ''

        if value =='':
            url = "http://" + str(host) + "/cgi-bin/camctrl/camctrl.cgi"
            data = urllib.parse.urlencode(cgi_parameter)

            request = urllib.request.Request(url, data.encode())
        else:
            url = "http://" + str(host) + "/cgi-bin/camctrl/camctrl.cgi?" + str(cgi_parameter) + "=" + str(value)
            request = urllib.request.Request(url)


        request.add_header("Authorization", "Basic " + encode_str.decode())
        response = urllib.request.urlopen(request, timeout=timeout)
        cgi_response = response.read()
        cgi = re.split(b"\\r\\n", response.read())
        print(cgi_response)
        return cgi[0].decode("utf-8")




    def get_model_name(self,host):
        model_name = self.get_cgi(host, 'system_info_modelname')
        model_name = model_name.replace('system_info_modelname=', '')
        model_name = model_name.replace('\r\n', '')
        model_name = model_name.replace('\'', '')
        return model_name

    def get_nmedia_stream(self,host):
        nmedia_stream = self.get_cgi(host, 'capability_nmediastream')
        nmedia_stream = nmedia_stream.replace('capability_nmediastream=', '')
        nmedia_stream = nmedia_stream.replace('\r\n', '')  # delete noise of string , not sure for all model
        nmedia_stream = nmedia_stream.replace('\'', '')  # delete noise of string ,not sure for all model
        return nmedia_stream #return string

    def get_videoclip_maxsize(self,host):
        video_maxsize = self.get_cgi(host, 'capability_media_videoclip_maxsize')
        video_maxsize = video_maxsize.replace('capability_media_videoclip_maxsize=', '')
        video_maxsize = video_maxsize.replace('\r\n', '')
        video_maxsize = video_maxsize.replace('\'', '')
        return video_maxsize


    def get_section_data(self, request):
        host = request.GET['camera_ip']
        self.camera_account = request.GET['camera_account']
        self.camera_passwd = request.GET['camera_password']
        tester = request.GET['tester']
        test_type = request.GET['test_type']
        camera_type = request.GET['camera_type']
        location = request.GET['test_location']
        return host, tester, test_type, camera_type, location


    def set_cgi_setpm3d(self, host, cgi_parameter, value='',timeout=30):

        '''for /cgi-bin/admin/setpm3d.cgi? use'''
        if not self.camera_passwd == '':
            auth_str = self.camera_account + ":" + self.camera_passwd
            auth_str = auth_str.replace('\n', '')
            auth_byte_str = auth_str.encode(encoding="utf-8")
            encode_str = base64.b64encode(auth_byte_str)
        else:
            encode_str = ''

        if value =='':
            url = "http://" + str(host) + "/cgi-bin/admin/setpm3d.cgi"
            data = urllib.parse.urlencode(cgi_parameter)

            request = urllib.request.Request(url, data.encode())
        else:
            url = "http://" + str(host) + "/cgi-bin/admin/setpm3d.cgi?" + str(cgi_parameter) + "=" + str(value)
            request = urllib.request.Request(url)


        request.add_header("Authorization", "Basic " + encode_str.decode())
        response = urllib.request.urlopen(request, timeout=timeout)
        cgi_response = response.read()
        cgi = re.split(b"\\r\\n", response.read())
        print(cgi_response)
        return cgi[0].decode("utf-8")



    # index 0 in server list
    def set_email_server(self , host , tester ):
        object = Email_server_private_parameter.objects.get(owner=tester)
        self.set_cgi(host , 'server_i0_name', 'Email')
        self.set_cgi(host, 'server_i0_type', 'email')
        self.set_cgi(host, 'server_i0_email_senderemail', object.server_i0_email_senderemail)
        self.set_cgi(host, 'server_i0_email_recipientemail', object.server_i0_email_recipientemail)
        self.set_cgi(host, 'server_i0_email_address', object.server_i0_email_address)
        self.set_cgi(host, 'server_i0_email_username', object.server_i0_email_username)
        self.set_cgi(host, 'server_i0_email_passwd', object.server_i0_email_passwd)
        self.set_cgi(host, 'server_i0_email_port', object.server_i0_email_port)
        self.set_cgi(host, 'server_i0_email_sslmode', object.server_i0_email_sslmode)

    # index 1 in server list
    def set_ftp_server(self , host , tester , test_type , location):
        object = Ftp_server_private_parameter.objects.get(owner=tester , test_type=test_type, location= location)
        model_name=self.get_model_name(host)
        self.set_cgi(host, 'server_i1_name', 'FTP')
        self.set_cgi(host, 'server_i1_type', 'ftp')
        self.set_cgi(host, 'server_i1_ftp_address', object.server_i1_ftp_address)
        self.set_cgi(host, 'server_i1_ftp_port', '21')
        self.set_cgi(host, 'server_i1_ftp_username', object.server_i1_ftp_username)
        self.set_cgi(host, 'server_i1_ftp_passwd', object.server_i1_ftp_passwd)
        self.set_cgi(host, 'server_i1_ftp_location', object.server_i1_ftp_location + model_name)
        self.set_cgi(host, 'server_i1_ftp_passive', '1')

    # index 2 in server list
    def set_nas_server(self, host, tester, test_type, location):
        model_name = self.get_model_name(host)
        object = Nas_server_private_parameter.objects.get(owner=tester, test_type=test_type, location=location)
        self.set_cgi(host, 'server_i2_name', 'NAS')
        self.set_cgi(host, 'server_i2_type', 'ns')
        self.set_cgi(host, 'server_i2_ns_location', object.server_i2_ns_location +'\\'+ model_name)
        self.set_cgi(host, 'server_i2_ns_workgroup', object.server_i2_ns_workgroup)
        self.set_cgi(host, 'server_i2_ns_username', object.server_i2_ns_username)
        self.set_cgi(host, 'server_i2_ns_passwd', object.server_i2_ns_passwd)



    def set_privacy_mask(self, host, camera_type):
        if not camera_type == 'SD' :
            parameter = {
                         'privacymask_c0_win_i1_enable': '1', 'privacymask_c0_win_i1_name': '1','privacymask_c0_win_i1_polygon': '60,0,70,0,70,240,60,240',
                         'privacymask_c0_win_i2_enable': '1', 'privacymask_c0_win_i2_name': '2','privacymask_c0_win_i2_polygon': '250,0,260,0,260,240,250,240',
                         'privacymask_c0_win_i3_enable': '1', 'privacymask_c0_win_i3_name': '3','privacymask_c0_win_i3_polygon': '0,60,320,60,320,70,0,70',
                         'privacymask_c0_win_i4_enable': '1', 'privacymask_c0_win_i4_name': '4','privacymask_c0_win_i4_polygon': '0,170,320,170,320,180,0,180'
                        }
            self.set_cgi(host, parameter)

        else:
            self.set_cgi_camctrl(host,'move','home')#PTZ to home point

            parameter = {
                        'method': 'add', 'maskname': '1','maskheight': '180','maskwidth': '30',
                        }
            self.set_cgi_setpm3d(host,parameter)

            parameter = {
                         'method': 'add', 'maskname': '2', 'maskheight': '30', 'maskwidth': '320',
                        }
            self.set_cgi_setpm3d(host, parameter)



    def set_motion_window(self,host,test_type):
        if test_type =='Stress_Test':
            sensitivity = '100'
        elif test_type =='Stability_Test':
            sensitivity = '85'
        parameter={
                   'motion_c0_win_sensitivity': sensitivity ,
                   'motion_c0_win_i0_enable':'1','motion_c0_win_i0_name':'Motion1','motion_c0_win_i0_polygonstd':'1000,2000,1000,4000,4000,4000,4000,2000','motion_c0_win_i0_objsize':'15',
				   'motion_c0_win_i1_enable':'1','motion_c0_win_i1_name':'Motion2','motion_c0_win_i1_polygonstd':'1000,6000,1000,8000,4000,8000,4000,6000','motion_c0_win_i1_objsize':'15',
				   'motion_c0_win_i2_enable':'1','motion_c0_win_i2_name':'Motion3','motion_c0_win_i2_polygonstd':'5000,2000,5000,8000,6000,8000,6000,2000','motion_c0_win_i2_objsize':'15',
				   'motion_c0_win_i3_enable':'1','motion_c0_win_i3_name':'Motion4','motion_c0_win_i3_polygonstd':'7000,2000,7000,4000,9000,4000,9000,2000','motion_c0_win_i3_objsize':'15',
				   'motion_c0_win_i4_enable':'1','motion_c0_win_i4_name':'Motion5','motion_c0_win_i4_polygonstd':'7000,6000,7000,8000,9000,8000,9000,6000','motion_c0_win_i4_objsize':'15'
                  }
        self.set_cgi(host, parameter)


    def set_media(self,host):
        model_name = self.get_model_name(host)
        video_maxsize=self.get_videoclip_maxsize(host)
        nmedia_stream=self.get_nmedia_stream(host)
        snapshot_source_index = int(nmedia_stream) - 1 # snapshot source define last stream

        parameter = {
                    #for crate snapshot , index 0 in media list
                    'media_i0_name':'snapshot' , 'media_i0_type':'snapshot' , 'media_i0_snapshot_source': snapshot_source_index ,'media_i0_snapshot_preevent':'7' , 'media_i0_snapshot_postevent':'7' ,
                    'media_i0_snapshot_prefix': model_name+'-' , 'media_i0_snapshot_datesuffix':'1',

     #               #for create video clip , index 1 in media list
                    'media_i1_name':'video clip' , 'media_i1_type':'videoclip' , 'media_i1_videoclip_preevent':'9' , 'media_i1_videoclip_maxduration':'20',
                    'media_i1_videoclip_maxsize':video_maxsize,'media_i1_videoclip_prefix': model_name+'_'+'clip-',

                    #for create syslog , index 2 in media list
                    'media_i2_name':'system log' , 'media_i2_type':'systemlog'
                    }

        self.set_cgi(host, parameter)


    def set_reboot_event(self,host):
        self.set_cgi(host, "event_i0_name", 'system_boot')
        self.set_cgi(host, "event_i0_trigger", 'boot')
        self.set_cgi(host, "event_i0_action_cf_enable", '1')# for SD card
        self.set_cgi(host, "event_i0_action_cf_media", '2')
        self.set_cgi(host, "event_i0_action_server_i0_enable", '1')  # for mail server
        self.set_cgi(host, "event_i0_action_server_i0_media", '2')
        self.set_cgi(host, "event_i0_action_server_i1_enable", '1')  # for ftp server
        self.set_cgi(host, "event_i0_action_server_i1_media", '2')
        self.set_cgi(host, "event_i0_action_server_i2_enable", '1')# for nas server
        self.set_cgi(host, "event_i0_action_server_i2_media", '2')
        self.set_cgi(host, "event_i0_action_server_i2_datefolder", '1')


    def set_motion_event(self,host):
        check_trigger_motion_window='00011111'#LSB is motion window 0
        check_trigger_motion_window=int(check_trigger_motion_window,2)
        check_trigger_motion_window=str(check_trigger_motion_window)
        self.set_cgi(host, "event_i1_name", 'video_motion_detection')
        self.set_cgi(host, "event_i1_trigger", 'motion')
        self.set_cgi(host, "event_i1_mdwin", check_trigger_motion_window)
        self.set_cgi(host, "event_i1_action_cf_enable", '1')  # for SD card
        self.set_cgi(host, "event_i1_action_cf_media", '1')
        self.set_cgi(host, "event_i1_action_server_i0_enable", '1')  # for mail server
        self.set_cgi(host, "event_i1_action_server_i0_media", '1')
        self.set_cgi(host, "event_i1_action_server_i1_enable", '1')  # for ftp server
        self.set_cgi(host, "event_i1_action_server_i1_media", '1')
        self.set_cgi(host, "event_i1_action_server_i2_enable", '1')  # for nas server
        self.set_cgi(host, "event_i1_action_server_i2_media", '1')
        self.set_cgi(host, "event_i1_action_server_i2_datefolder", '1')

    def set_preiodically_event(self,host,test_type):
        stress_inter='1'
        stability_inter='10'
        self.set_cgi(host, "event_i2_name", 'Periodically')
        self.set_cgi(host, "event_i2_trigger", 'seq')

        if test_type =='Stress_Test':
            self.set_cgi(host, "event_i2_inter", stress_inter)
        elif test_type =='Stability_Test':
            self.set_cgi(host, "event_i2_inter", stability_inter)

        self.set_cgi(host, "event_i2_action_cf_enable", '1')  # for SD card
        self.set_cgi(host, "event_i2_action_cf_media", '0')
        self.set_cgi(host, "event_i2_action_server_i0_enable", '1')  # for mail server
        self.set_cgi(host, "event_i2_action_server_i0_media", '0')
        self.set_cgi(host, "event_i2_action_server_i1_enable", '1')  # for ftp server
        self.set_cgi(host, "event_i2_action_server_i1_media", '0')
        self.set_cgi(host, "event_i2_action_server_i2_enable", '1')  # for nas server
        self.set_cgi(host, "event_i2_action_server_i2_media", '0')
        self.set_cgi(host, "event_i2_action_server_i2_datefolder", '1')

    def set_recording_sd(self,host,test_type):
        recording_maxsize='2000'
        recording_maxduration='3600'#second

        model_name=self.get_model_name(host)
        nmedia_stream=self.get_nmedia_stream(host)
        last_stream_index = str(int(nmedia_stream) - 1)
        first_stream_index = '0'
        prefix_name=model_name+'-'

        self.set_cgi(host, "disk_i0_cyclic_enabled", '1')
        self.set_cgi(host, "recording_i0_name", 'SD')
        self.set_cgi(host, "recording_i0_dest", 'cf')
        self.set_cgi(host, "recording_i0_maxduration", recording_maxduration)
        self.set_cgi(host, "recording_i0_maxsize", recording_maxsize)
        self.set_cgi(host, "recording_i0_prefix", prefix_name )

        if test_type =='Stress_Test':
            self.set_cgi(host, "recording_i0_source", first_stream_index)
        elif test_type =='Stability_Test':
            self.set_cgi(host, "recording_i0_source", last_stream_index)

    def set_recording_nas(self,host):# it should call set_nas_server() first before call this function
        reserved_space='1000'  #Byte
        recording_maxsize = '2000' #Byte
        recording_maxduration = '3600' #second
        model_name = self.get_model_name(host)
        nmedia_stream = self.get_nmedia_stream(host)
        prefix_name=model_name+'-'
        last_stream_index = str(int(nmedia_stream) - 1)
        self.set_cgi(host, "recording_i1_name", 'NAS')
        self.set_cgi(host, "recording_i1_dest", '2')
        self.set_cgi(host, "recording_i1_limitsize", '1')
        self.set_cgi(host, "recording_i1_reserveamount", reserved_space)
        self.set_cgi(host, "recording_i1_maxduration", recording_maxduration)
        self.set_cgi(host, "recording_i1_maxsize", recording_maxsize)
        self.set_cgi(host, "recording_i1_prefix", prefix_name)
        self.set_cgi(host, "recording_i1_cyclic", '1')
        self.set_cgi(host, "recording_i1_source", last_stream_index)




















































































