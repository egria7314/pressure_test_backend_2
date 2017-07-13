from camera_log.telnet_module import URI

class SDPrefix():
    def __init__(self, camera_ip, camera_name, camera_password ):
        self.camera_ip = camera_ip
        self.camera_name = camera_name
        self.camera_password = camera_password


    def get_recording_type(self):
        """Get nas location from camera by cgi"""
        type_code = None
        for index in range(2):
            command = 'http://'+self.camera_ip+'/cgi-bin/admin/getparam.cgi?recording_i{0}_dest'.format(index)
            try:
                url = URI.set(command, self.camera_name, self.camera_password)
                url = url.read().decode('utf-8').split("\r\n")
                result = url[0].replace('recording_i{0}_dest'.format(index), '').replace("'", "").replace("=", "")
                if result == 'cf':
                    type_code = index
                    break
                else:
                    continue
            except:
                type_code = 'get recording type error'

        return type_code

    def get_recording_prefix(self):
        """Get nas location from camera by cgi"""
        index = self.get_recording_type()
        command = 'http://'+self.camera_ip+'/cgi-bin/admin/getparam.cgi?recording_i{0}_prefix'.format(index)

        prefix = None
        try:
            url = URI.set(command, self.camera_name, self.camera_password)
            url = url.read().decode('utf-8').split("\r\n")
            result = url[0].replace('recording_i{0}_prefix'.format(index), '').replace("'", "").replace("=", "")
            prefix = result
        except:
            prefix = 'get recording prefix error'
        finally:
            return prefix