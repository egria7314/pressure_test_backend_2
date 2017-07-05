# -*- coding: utf-8 -*-
from collections import namedtuple
from collections import defaultdict
from multiprocessing import Pool
from PIL import Image
import os
import glob
import cv2
import numpy as np
import json
import platform
import pexpect
import time

from broken_tests.helpers.roi_module import RoiModule
from broken_tests.helpers import common
from broken_tests.helpers.http_module import URI
from broken_tests.tasks import check_single_image_as_usual
from celery import group
from celery.result import allow_join_result


BoxBorder = namedtuple('BoxBorder', 'left, upper, right, lower')


class ContentAnalysis(object):
    def __init__(self):
        pass

    def __call__(self, ip, user, password):
        """Set up referenced camera to get more infomation.

        Keyword arguments:
        ip -- camera ip
        user -- camera username
        password -- camera password

        """
        self.__ref_cam_ip = ip
        self.__ref_cam_user = user
        self.__ref_cam_pwd = password
        return self
    
    def lines_detection(self, objImage, box):
        """Return line info(rho, theta) by Hough line detection.

        Keyword arguments:
        objImage -- an image object read from Pilow module
        box -- a 4-tuple subregion of image to detect

        """
        # Using python openCV
        pil_img = objImage.crop(box).convert('RGB')
        cv_img = np.array(pil_img)
        cv_img = cv2.cvtColor(cv_img, cv2.COLOR_RGB2GRAY)

        blur = cv2.GaussianBlur(cv_img, (5, 5), 0)
        # cv2.imwrite("/home/dqa/data/pressure_test/clips/helpers/blur.jpg", blur)
        edges = cv2.Canny(blur, 5, 10)
        # cv2.imwrite("/home/dqa/data/pressure_test/clips/helpers/canny.jpg", edges)

        minLineLength = int(box.lower*0.3) if box.lower > box.right else int(box.right*0.3)
        lines = cv2.HoughLines(edges, 1, np.pi/180, minLineLength)
        # print( "1st:", lines[0], "2nd:", lines[1], "size:", lines.size )

        return lines if not isinstance(lines, type(None)) else np.array([])

    
    def count_horizontal_lines(self, box, lineCount, objImage):
        """Return True if number of horizontal lines are equal to lineCount.

        Keyword arguments:
        box -- a 4-tuple subregion of image to detect
        lineCount -- the number of expected lines
        objImage -- an image object read from Pilow module

        """
        BOARDER_BUF = 10
        HORIZONTAL_ANGEL = round(np.pi/2, 2)

        detected_lines = self.lines_detection(objImage, BoxBorder(
            box.left,
            box.upper-BOARDER_BUF,
            box.right,
            box.lower+BOARDER_BUF
            )
        )

        listOfRhoAndTheta = detected_lines.flatten()
        listOfTheta = map(lambda theta: round(theta, 2), listOfRhoAndTheta[1::2].tolist())

        return bool(detected_lines.size) and (lineCount <= len(detected_lines)) \
            and (list(listOfTheta).count(HORIZONTAL_ANGEL) >= lineCount) 
    

    def count_vertical_lines(self, box, lineCount, objImage):
        """Return True if number of vertical lines are equal to lineCount.

        Keyword arguments:
        box -- a 4-tuple subregion of image to detect
        lineCount -- the number of expected lines
        objImage -- an image object read from Pilow module

        """
        BOARDER_BUF = 10
        VERTICAL_ANGEL = 0.

        detected_lines = self.lines_detection(objImage, BoxBorder(
            box.left-BOARDER_BUF,
            box.upper,
            box.right+BOARDER_BUF,
            box.lower
            )
        )

        listOfRhoAndTheta = detected_lines.flatten()
        listOfTheta = map(lambda theta: round(theta, 2), listOfRhoAndTheta[1::2].tolist())

        return bool(detected_lines.size) and (lineCount <= len(detected_lines)) \
            and (list(listOfTheta).count(VERTICAL_ANGEL) >= lineCount)
    

    def check_no_broken_pixel(self, box, objImage):
        """Return True if there is no edge detected in subregion of image.

        Keyword arguments:
        box -- a 4-tuple subregion of image to detect
        objImage -- an image object read from Pilow module

        """
        # Using pyhton openCV
        pil_img = objImage.crop(box).convert('RGB')
        cv_img = np.array(pil_img)

        # Convert RGB to BGR
        cv_img = cv2.cvtColor(cv_img, cv2.COLOR_RGB2GRAY)
        # cv2.imwrite("/home/dqa/data/pressure_test/clips/helpers/crop.jpg", cv_img)

        # Smooth image
        blur = cv2.GaussianBlur(cv_img, (5, 5), 0)
        # cv2.imwrite("/home/dqa/data/pressure_test/clips/helpers/blur.jpg", blur)
        edges = cv2.Canny(blur, 100, 200)
        # cv2.imwrite("/home/dqa/data/pressure_test/clips/helpers/canny.jpg", edges)

        # Indent region to Only has black pixel inside mask
        mask = np.zeros(edges.shape[:2], np.uint8)
        height, width = edges.shape[:2]

        indent_height = 2 if height > width else 5
        indent_width = 5 if height > width else 2
        percentage_of_all_black_area = 1.0

        mask[indent_height:height-indent_height, indent_width:width-indent_width] = 255
    
        hist = cv2.calcHist([edges], [0], mask, [256], [0, 256])

        return hist[0] >= (width-2*indent_width) * (height-2*indent_height) * percentage_of_all_black_area


    def cut_to_frames(self, clipPath, dstFolder):
        """Output frames by 1 fps from video sequence.

        Keyword arguments:
        clipPath -- path of video sequence
        dstFolder -- directory path of output frames

        """
        # video sequence to frame pictures
        v = common.Video(clipPath)
        v.to_multi_frames(2, os.path.join(dstFolder, "mul%05d.jpg"))
        return glob.glob(os.path.join(dstFolder, 'mul[0-9]*.jpg'))

    
    def trans_from_points_to_box(self, pointsRepr):
        """Translate rectangle notation from (x1, y1, x2, y2, x3, y3, x4, y4)
            to (left, upper, right, lower).

        (x1,y1) (x2,y2)
           *-------*
           |       |
           |       |
           *-------*
        (x4,y4) (x3,y3)

        to (left, upper, right, lower)

        Keyword arguments:
        pointsRepr -- the list of 4 corners (format [x1, y1, x2, y2, x3, y3, x4, y4])

        """
        left, upper, right, lower = pointsRepr[0], pointsRepr[1], pointsRepr[2], pointsRepr[7] + 1
        return BoxBorder(left, upper, right, lower)


    def check_single_image_as_usual(self, params):
        """Return True if image detected as usual.

        Keyword arguments:
        params -- the pair with privacy masks and image path 

        Return:
        dict -- the return value, including literal blocks::
            {
                'result': the string of frame result,
                'frame_path': the string of frame path,
                'error_boxes': the string of broken BoxBoarder, ex: "BoxBorder(1, 2, 3,4), BoxBorder(1, 2, 3,4)"
            }
        """
        privacy_masks, imgPath = params
        # print("PRIVACY_MASK: ", privacy_masks)
        # print("IMAGE_PATH: ", imgPath)
        if len(privacy_masks) > 0:
            ret = {'result': 'passed', 'frame_path': imgPath, 'error_boxes': None}
        else:
            ret = {'result': 'failed', 'frame_path': imgPath, 'error_boxes': "Without any box"}
        print("READDDD before: ", imgPath)
        img = Image.open(imgPath)
        print("READDDD succ: ", imgPath)
        for i, mask in enumerate(privacy_masks):
            # normal_frame = self.check_no_broken_pixel(mask, img) and self.check_lines(mask, 2, img)
            normal_frame = self.check_no_broken_pixel(mask, img)
            # print mask, normal_frame
            if not normal_frame:
                 ret['result'] = 'failed'
                 ret['error_boxes'] = ",".join(list(filter(None, [ ret['error_boxes'], str(mask) ]) ))
        
        # delete normal frame
        if ret['result'] == 'passed':
            os.remove(imgPath)

        return ret


    # def check_single_image_as_usual_loop(self, params):
    #     """Return True if image detected as usual.

    #     Keyword arguments:
    #     params -- the pair with privacy masks and image path 
    #     """
    #     privacy_masks, group_of_image_paths = params
    #     # print("PRIVACY_MASK: ", privacy_masks)
    #     # print("GROUP_OF_IMAGE_PATH: ", group_of_image_paths)
    #     failed_messages = []
    #     mask_order = ["Left", "Right", "Down", "Up"]

    #     for imgPath in sorted(group_of_image_paths):
    #         img = Image.open(imgPath)
    #         for i, mask in enumerate(privacy_masks):
    #             # normal_frame = self.check_no_broken_pixel(mask, img) and self.check_lines(mask, 2, img)
    #             normal_frame = self.check_no_broken_pixel(mask, img)
    #             # print mask, normal_frame
    #             if not normal_frame:
    #                 msg = "{filename} : {mask_title}\n".format(filename=imgPath, mask_title=mask_order[i])
    #                 failed_messages.append(msg)

    #     return failed_messages


    # def chunks(self, chunkable, chunk_num):
    #     """ Yield successive n-sized chunks from l.
    #     """
    #     avg = len(chunkable) / float(chunk_num)
    #     last = 0.0

    #     while last < len(chunkable):
    #         yield chunkable[int(last):int(last + avg)]
    #         last += avg

    
    def get_actual_privacy_masks_coordinates(self, recDstType):
        """Return the actual privacy mask coordinates

        Keyword arguments:
        recDstType -- the string of recording destination server type. Now we have 2 available values SD and NAS.

        """
        # transform mask position
        roi = RoiModule(self.__ref_cam_ip, self.__ref_cam_user, self.__ref_cam_pwd, recDstType)
        privacy_masks = list(map(self.trans_from_points_to_box, roi.return_mask()))
        
        return privacy_masks


    # # @save_exception_to('fw_pressure_test.content_analysis', os.path.join(os.path.dirname( __file__ ), 'content_analysis.log'))
    # # @dump_return_message_to_console
    # def check_video_frames_as_usual_v2(self, framesFolderPath, privacyMasks):
    #     """Return True if the video sequence detected by 1 fps is not unusual.
        
    #     v2 is with multiprocessing module.
        
    #     Keyword arguments:
    #     framesFolderPath -- the string of directory path to extracted video frames 
        
    #     """
    #     failed_filenames = []
    #     frames = glob.glob(os.path.join(framesFolderPath, '*.jpg'))

    #     if not frames:
    #         return json.dumps(self.response_message("failed", framesFolderPath, failed_filenames), ensure_ascii=False)

    #     # transform mask position
    #     privacy_masks = privacyMasks
        
    #     # do verifying        
    #     nbr_samples_in_total = len(frames)
    #     nbr_parallel_blocks = 1
    #     pool = Pool(processes=nbr_parallel_blocks)
    #     nbr_in_failed_filenames = pool.map(self.check_single_image_as_usual_loop,
    #                             zip([privacy_masks]*nbr_parallel_blocks, self.chunks(sorted(frames), nbr_parallel_blocks)))
        
    #     failed_filenames = [fn for i in range(nbr_parallel_blocks) for fn in nbr_in_failed_filenames[i]]

    #     status  = 'failed' if len(failed_filenames) > 0 else 'passed'

    #     return json.dumps(self.response_message(status, framesFolderPath, failed_filenames), ensure_ascii=False)
    

    def check_video_frames_as_usual_v3(self, framesFolderPath, privacyMasks):
        """Return True if the video sequence detected by 1 fps is not unusual.
        
        v3 is with celery group module.
        
        Keyword arguments:
        framesFolderPath -- the string of directory path to extracted video frames 
        
        Return:
        dict -- the return value, including literal blocks::
            {
                'result': the string of video result,
                'failed_frames': the list of check_single_image_as_usual dict to indicate failed frames info 
            }
        
        """
        # collect frames
        frames = glob.glob(os.path.join(framesFolderPath, '*.jpg'))

        if not frames:
            return { 'result': 'failed', 'failed_frames': [] }
            
        # transform mask position
        privacy_masks = privacyMasks
        
        # concurrent do verifying
        print("BEGIN PIPELINE+++++++++++++++++")
        job = group(check_single_image_as_usual.s(privacy_masks, frame) for frame in sorted(frames) )
        result = job.apply_async()
        # [See Ref] https://stackoverflow.com/questions/33280456/calling-async-result-get-from-within-a-celery-task
        # to avoid RuntimeError: Never call result.get() within a task!
        with allow_join_result():    
            video_summary = result.get()      
        # print( "video_summary: ", video_summary )
        print("END PIPELINE+++++++++++++++++")
        is_usual = all(map(lambda x: x == 'passed', [ each_frame['result'] for each_frame in video_summary ]))
        status = 'passed' if is_usual else 'failed'
        
        # add broken frame info        
        broken_frames_list = [] if status == 'passed' else self.filter_broken_frames_to_list(video_summary)

        print( "broken_frames_list: ", broken_frames_list )
        return { 'result': status, 'failed_frames': broken_frames_list }
    

    def check_video_frames_as_usual_v4(self, framesFolderPath, privacyMasks):
        """Return True if the video sequence detected by 1 fps is not unusual.
        
        v3 is with celery group module.
        
        Keyword arguments:
        framesFolderPath -- the string of directory path to extracted video frames 
        
        Return:
        dict -- the return value, including literal blocks::
            {
                'result': the string of video result,
                'failed_frames': the list of check_single_image_as_usual dict to indicate failed frames info 
            }
        
        """
        # collect frames
        frames = glob.glob(os.path.join(framesFolderPath, '*.jpg'))

        if not frames:
            return { 'result': 'failed', 'failed_frames': [] }
            
        # transform mask position
        privacy_masks = privacyMasks
        
        # concurrent do verifying
        print("BEGIN V4+++++++++++++++++")
        video_summary = []
        for frame in sorted(frames):
            video_summary.append(self.check_single_image_as_usual((privacy_masks, frame)))
        
        print("END V4+++++++++++++++++")
        is_usual = all(map(lambda x: x == 'passed', [ each_frame['result'] for each_frame in video_summary ]))
        status = 'passed' if is_usual else 'failed'
        
        # add broken frame info        
        broken_frames_list = [] if status == 'passed' else self.filter_broken_frames_to_list(video_summary)

        print( "broken_frames_list: ", broken_frames_list )
        return { 'result': status, 'failed_frames': broken_frames_list }

    
    def check_video_frames_as_usual_v5(self, framesFolderPath, privacyMasks):
        """Return True if the video sequence detected by 1 fps is not unusual.
        
        v3 is with celery group module.
        
        Keyword arguments:
        framesFolderPath -- the string of directory path to extracted video frames 
        
        Return:
        dict -- the return value, including literal blocks::
            {
                'result': the string of video result,
                'failed_frames': the list of check_single_image_as_usual dict to indicate failed frames info 
            }
        
        """
        # collect frames
        frames = glob.glob(os.path.join(framesFolderPath, '*.jpg'))

        if not frames:
            return { 'result': 'failed', 'failed_frames': [] }
            
        # transform mask position
        privacy_masks = privacyMasks
        
        # concurrent do verifying
        print("BEGIN PIPELINE+++++++++++++++++")
        for frame in sorted(frames):
            result = check_single_image_as_usual.apply_async(args=[privacy_masks, frame], queue='check_single_image_inside_{}'.format(os.path.dirname(frame)))
        while not result.ready():
            time.sleep(5)
        video_summary = result.get()      
        # print( "video_summary: ", video_summary )
        print("END PIPELINE+++++++++++++++++")
        is_usual = all(map(lambda x: x == 'passed', [ each_frame['result'] for each_frame in video_summary ]))
        status = 'passed' if is_usual else 'failed'
        
        # add broken frame info        
        broken_frames_list = [] if status == 'passed' else self.filter_broken_frames_to_list(video_summary)

        print( "broken_frames_list: ", broken_frames_list )
        return { 'result': status, 'failed_frames': broken_frames_list }


    def filter_broken_frames_to_list(self, all_frames):
        """
        """
        print("debug all frames: ", all_frames)
        formated_broken_frames_list = []
        broken_frames = list(filter(lambda f: f['result'] == 'failed', all_frames))
        print("debug broken frame: ", broken_frames)
        for each_frame in broken_frames:
            print("each_frame in broken frames: ", each_frame)
            broken_frame_info = {
                    'path': each_frame['frame_path'],
                    'error_message': each_frame['error_boxes']
            }

            formated_broken_frames_list.append(broken_frame_info)
        
        print("formated_broken_frames_list: ", formated_broken_frames_list)
        return formated_broken_frames_list


    def save_snapshot_to_dir(self, framesFolderPath, streamId):
        """
        """
        FILENAME = 'sample.jpg'
        SNAPSHOT_PATH = os.path.join(framesFolderPath, FILENAME)
        uri = 'http://{}/cgi-bin/viewer/video.jpg?streamid={}'.format(self.__ref_cam_ip, streamId)
        context = URI.set(uri, self.__ref_cam_user, self.__ref_cam_pwd)
        if not os.path.exists(framesFolderPath):
            os.makedirs(framesFolderPath)

        with open(SNAPSHOT_PATH, 'wb') as fp:
            fp.write(context.read())
        
        return SNAPSHOT_PATH


    # def response_message(self, status, framesFolderPath, failed_filenames):
    #     """Return Dict according by status.

    #     Keyword arguments:
    #     status -- the string of testing result. Now Only 'passed' or 'failed'. 
    #     failed_filenames -- the list of failed filename.
    #     """
    #     recheck_msg = "[Broken Images]\n {some_of_filenames}\n More than {num} frames failed...\n We suggest you check this video manually or recheck your test environment."
    #     displayed_limit = 120
        
    #     ret = defaultdict(str)
    #     ret['analysis_result'] = status

    #     is_failed_by_empty_folder = True if status == 'failed' and len(failed_filenames) <= 0 else False
    #     get_empty_folder_msg = lambda x: "[Broken Images]\n {folder} is empty\n".format(folder=x)
        
    #     is_failed_by_error_frames = True if status == 'failed' and len(failed_filenames) > 0 else False
        
    #     # If failed_filenames are too much, we set a displayed limit number
    #     get_failed_msg = lambda x, displayed_limit, template_msg: "[Broken Images]\n  {filename} \n".format(filename="\n".join(x)) if len(x) < displayed_limit else template_msg.format(some_of_filenames="\n".join(x[0:displayed_limit]), num=len(x)) 
        
    #     is_passed = True if status == 'passed' else False
    #     get_passed_msg = lambda x: "{}".format(x)

    #     ret['message'] = (is_failed_by_empty_folder and get_empty_folder_msg(framesFolderPath)) or \
    #         (is_failed_by_error_frames and get_failed_msg(failed_filenames, displayed_limit, recheck_msg)) or \
    #         (is_passed and get_passed_msg("-"))

       
    #     return dict(ret)
    

    # def response_message_v3(self, status, failed_frames_list):
    #     """Return Dict according by status.

    #     Keyword arguments:
    #     status -- the string of testing result. Now Only 'passed' or 'failed'. 
    #     failed_filenames -- the list of failed filename.
    #     """
    #     ret = {}
    #     ret['result'] = status

    #     is_failed_by_empty_folder = True if status == 'failed' and len(failed_frames_list) <= 0 else False
    #     get_empty_folder_msg = lambda x: "{folder} is empty\n".format(folder=x)
        
    #     is_failed_by_error_frames = True if status == 'failed' and len(failed_frames_list) > 0 else False
        
    #     # If failed_filenames are too much, we set a displayed limit number
    #     get_failed_msg = lambda x: "{folder} has broken images\n".format(folder=x) 
    #     print( "failed_filenames: ", failed_filenames)
    #     print( "framesFolderPath: ", framesFolderPath)
    #     failed_filenames = []
    #     for f in failed_filenames:
    #         file['path'] = os.path.join(framesFolderPath, f)
    #         file['error_message'] = 
    #     get_failed_filenames = [ os.path.join(framesFolderPath, f) for f in failed_filenames ]
    #     ret['failed_frames'] = get_failed_filenames

    #     is_passed = True if status == 'passed' else False
    #     get_passed_msg = lambda x: "{}".format(x)

    #     ret['error_message'] = (is_failed_by_empty_folder and get_empty_folder_msg(framesFolderPath)) or \
    #         (is_failed_by_error_frames and get_failed_msg(failed_filenames)) or \
    #         (is_passed and get_passed_msg(""))
        
    #     print( "ret: ", ret )
       
    #     return ret


    def mount_folder(self, remote_username, remote_password, remote_path, sudo_password, local_path):
        """
        """
        if platform.system() == 'Windows': return False
        
        if os.path.ismount(local_path): return True
        
        # create the new folder
        cmd = "mkdir {mounted_at}".format(mounted_at=local_path)
        p = pexpect.spawn(cmd)
        # p.expect(': ')
        # p.sendline(sudo_password)
        # p.expect( "\r\n" )

        # mount
        cmd = "mount -t cifs -o username={user},password={pwd} {remote_path} {local_path}".format(
            user=remote_username, pwd=remote_password,
            remote_path=remote_path, local_path=local_path)

        p = pexpect.spawn(cmd)
        # p.expect(': ')
        # p.sendline(sudo_password)
        # p.expect( "\r\n" )

        # wait mounting
        time.sleep(10)

        return os.path.ismount(local_path)

    def unmount_folder(self, local_path, sudo_password):
        """
        """
        if platform.system() == 'Windows': return False

        # umount
        cmd = "umount {local_path}".format(local_path=local_path)
        p = pexpect.spawn(cmd)
        # p.expect(': ')
        # p.sendline(sudo_password)
        # p.expect( "\r\n" )

        # remove folder
        time.sleep(10)
        if not os.path.ismount(local_path):
            cmd = "rm -rf {mounted_at}".format(mounted_at=local_path)
            p = pexpect.spawn(cmd)
            # p.expect(': ')
            # p.sendline(sudo_password)
            # p.expect( "\r\n" )

        if os.path.exists(local_path): return False

        return True