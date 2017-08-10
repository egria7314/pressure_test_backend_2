__author__ = 'carlos.hu'
# -*- coding: utf-8 -*-
from broken_tests.helpers.http_module import URI
# from http_module import URI
import re
import json

class RoiModule(object):
    def __init__(self, ip, account, password, video_destination):
        """
        Keyword arguments:
        ip -- the string of ip that is camera ip
        account -- the string of account that is camera account
        password -- the string of password that is camera password
        video_destination -- the string of video_destination that is the recording files destination
        """
        self.ip = ip
        self.account = account
        self.password = password
        self.video_destination = video_destination
        self.get_roi_position()


    def get_roi_position(self):
        """ Get five privacy mask position"""
        mask_position_dict = {}
        timestamp_mask_position_dict = {}

        command = 'http://'+self.ip+'/cgi-bin/admin/getparam.cgi?system_info_modelname'
        url = URI.set(command, self.account, self.password)
        resp = url.read().decode('utf-8')
        modelname = re.search('=\'(.*)\'', resp).groups()[0]
        print("MODEL: ", modelname)
        
        if 'SD' in modelname:
            mask_position_list = self.__get_mask_position_form_3D_mask()
        elif 'MS' in modelname or 'MA' in modelname:
            mask_position_list = self.__get_mask_position_from_rect()
        else:
            mask_position_list = self.__get_mask_position()

        for i in range(len(mask_position_list)):
            if len(mask_position_list[i]) == 8:
                mask_position_list[i][5] -= 1
                mask_position_list[i][7] -= 1
                mask_position_dict[str(i)] = mask_position_list[i]
        
        self.mask_position_dict = mask_position_dict

        # for i in range(len(mask_position_list)):
        #     mask_position_list[i][5] -= 1
        #     mask_position_list[i][7] -= 1

        # timestamp_mask_position_dict["mask_timestamp"] = mask_position_list[0]
        # mask_position_dict["mask_left"] = mask_position_list[1]
        # mask_position_dict["mask_right"] = mask_position_list[2]
        # mask_position_dict["mask_up"] = mask_position_list[3]
        # mask_position_dict["mask_down"] = mask_position_list[4]

        # self.mask_position_dict = mask_position_dict
        # self.timestamp_mask_position_dict = timestamp_mask_position_dict
    
    def return_mask(self):
        """ Return row and column privacy mask"""
        #print json.dumps(self.mask_position_dict, ensure_ascii=False)
        print('values: ', self.mask_position_dict.values())
        return self.mask_position_dict

    def return_timestamp_mask(self):
        """ Return timestamp privacy mask"""
        #print json.dumps(self.timestamp_mask_position_dict, ensure_ascii=False)
        return self.timestamp_mask_position_dict

    def __get_recording_source(self):
        """Get recording recording files source"""
        recording_information ={}
        command = 'http://'+self.ip+'/cgi-bin/admin/getparam.cgi?recording'
        url = URI.set(command, self.account, self.password)
        recording_data = url.read().decode('utf-8')
        recording_dest = re.findall("dest='(.+)'",recording_data)
        recording_source = re.findall("source='(.+)'",recording_data)
        #dest = cf =>SD card; dest = 2  =>NAS; VAST
        for i in range(len(recording_dest)):
            if recording_dest[i] == 'cf':
                recording_information['SD'] = str(recording_source[i])
            else:
                recording_information['NAS'] = str(recording_source[i])
        recording_information['VAST'] = '0'
        return recording_information[str(self.video_destination)]
    
    def get_recording_source(self):
        """Get recording recording files source"""
        return self.__get_recording_source()

    def __get_modelname(self):
        """Get camera modelname"""
        command = 'http://'+self.ip+'/cgi-bin/admin/getparam.cgi?system_info_modelname'
        url = URI.set(command, self.account, self.password)
        resp = url.read().decode('utf-8')
        modelname = re.search('=\'(.*)\'', resp).groups()[0]
        print("MODEL: ", modelname)
        return modelname

    def __get_resulotion(self):
        """ Get ratio of privacy mask setting to recording file resolution """
        modelname = self.__get_modelname()
        recording_source = self.__get_recording_source()
        command = 'http://'+self.ip+'/cgi-bin/admin/getparam.cgi?videoin_c0_s'+recording_source+'_resolution'
        url = URI.set(command, self.account, self.password)
        resolution = url.read().decode('utf-8')
        width = re.search('=\'(.*)x(.*)\'',resolution).groups()[0]
        height = re.search('=\'(.*)x(.*)\'',resolution).groups()[1]
        if 'MS' in modelname or 'MA' in modelname:
            w, h = 9999, 9999
        elif 'SD' in modelname:
            w = 320
            h = 240 if round(float(width)/float(height),2) == 1.33 else 180
        else:
            w, h = 320, 240
        print("w: ", w, "h: ", h)

        width_ratio = float(width)/w
        hight_ratio = float(height)/h
        return width_ratio,hight_ratio

    def __regulate_mask_position(self,mask_position):
        """ hight * hight_ratio & width * width_ratio
        Keyword arguments:
        mask_position -- The string of mask_position that is the position of privacy mask
        """
        ratio = self.__get_resulotion()
        width_ratio = ratio[0]
        hight_ratio = ratio[1]
        #print mask_position
        for mask_num in range(len(mask_position)):
            mask_position[mask_num] = mask_position[mask_num].split(',')
            for mask_position_num in range(0,len(mask_position[mask_num])-1,2):
                mask_position[mask_num][mask_position_num] = int(int(mask_position[mask_num][mask_position_num])*width_ratio)
                mask_position[mask_num][mask_position_num+1] = int(int(mask_position[mask_num][mask_position_num+1])*hight_ratio)
        return mask_position

    def __get_mask_position(self):
        """ Get privacy mask info in camera by cgi"""
        mask_position = []
        for i in range(5):
            command = 'http://'+self.ip+'/cgi-bin/admin/getparam.cgi?privacymask_c0_win_i'+str(i)+'_polygon'
            url = URI.set(command, self.account, self.password)
            response = url.read().decode('utf-8')
            mask_position.append(re.search(r'=\'(.*)\'', response).groups()[0])

        return self.__regulate_mask_position(mask_position)

    def __get_mask_position_form_3D_mask(self):
        """ Get 2 privacy masks info.
        Retrun 2 privacy mask represented by 4-coord.

        The 2 privacy masks must be located like cross on the centre of snapshot.
        
        """
        # Max plugin size 320x180
        PM_16_to_9 = ['150,0,170,0,170,180,150,180', '0,80,320,80,320,100,0,100']
        # Max plugin size 320x240
        PM_4_to_3 = ['150,0,170,0,170,240,150,240', '0,110,320,110,320,130,0,130']
        
        recording_source = self.__get_recording_source()
        command = 'http://'+self.ip+'/cgi-bin/admin/getparam.cgi?videoin_c0_s'+recording_source+'_resolution'
        url = URI.set(command, self.account, self.password)
        resolution = url.read().decode('utf-8')
        width = re.search('=\'(.*)x(.*)\'',resolution).groups()[0]
        height = re.search('=\'(.*)x(.*)\'',resolution).groups()[1]
        mask_position = PM_4_to_3 if round(float(width)/float(height),2) == 1.33 else PM_16_to_9
        
        return self.__regulate_mask_position(mask_position)

    def __get_mask_position_from_rect(self):
        """

        """
        mask_position = []
        for i in range(5):
            command = 'http://'+self.ip+'/cgi-bin/admin/getparam.cgi?privacymask_c0_win_i'+str(i)+'_rectanglestd'
            url = URI.set(command, self.account, self.password)
            response = url.read().decode('utf-8')
            left, top, width, height = re.search(r'=\'(.*)\'', response).groups()[0].split(',')
            left, top, width, height = int(left), int(top), int(width), int(height)
            print("left: ", left, "top: ", top, "width: ", width, "height: ", height)
            if (left+top+width+height) > 0:
                mask_position.append('{x1},{y1},{x2},{y2},{x3},{y3},{x4},{y4}'.format(
                    x1=left, y1=top,
                    x2=left+width, y2=top,
                    x3=left+width, y3=top+height,
                    x4=left, y4=top+height
                ))
        print("mask_postion: ", mask_position)
        return self.__regulate_mask_position(mask_position)