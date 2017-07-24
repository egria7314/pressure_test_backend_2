import unittest
from unittest.mock import patch, MagicMock
from broken_tests.helpers.content_analysis import ContentAnalysis
from PIL import Image
import os
from broken_tests.helpers import content_analysis as anly
import numpy as np
from broken_tests.helpers.roi_module import RoiModule
from io import BytesIO
from django.conf import settings
import shutil
# import json


class TestContentAnalysis(unittest.TestCase):
    def setUp(self):
        self.ca = ContentAnalysis()

    def test_2_lines_are_detected_in_pattern(self):
        img = Image.open(os.path.join(settings.BASE_DIR, 'unit_test/broken_tests/test_data/mul01.jpg'))
        buf = 10  # buffer to include edge
        box = anly.BoxBorder(left=480-buf, upper=0, right=560+buf, lower=1920)

        # each line has 2 elements(rho and theta)
        print( self.ca.lines_detection(img, box) )
        assert self.ca.lines_detection(img, box).size == 4

    def test_2_horizontal_lines_are_detected_in_pattern(self):
        img = Image.open(os.path.join(settings.BASE_DIR, 'unit_test/broken_tests/test_data/mul01.jpg'))
        buf = 10  # buffer to include edge
        h_box = anly.BoxBorder(left=0, upper=480-buf, right=2560, lower=560+buf)
        ca = ContentAnalysis()
        with patch.object(ca, 'lines_detection', return_value=np.array([[[10., 1.57]], [[55., 1.57]]])):
            got_2_lines = ca.count_horizontal_lines(h_box, 2, img)

        assert got_2_lines == True

    def test_2_vertical_lines_are_detected_in_pattern(self):
        img = Image.open(os.path.join(settings.BASE_DIR, 'unit_test/broken_tests/test_data/mul01.jpg'))
        buf = 10  # buffer to include edge
        v_box = anly.BoxBorder(left=480-buf, upper=0, right=560+buf, lower=1920)
        ca = ContentAnalysis()
        with patch.object(ca, 'lines_detection', return_value=np.array([[[10., 0.]], [[55., 0.]]])):
            got_2_lines = self.ca.count_vertical_lines(v_box, 2, img)

        assert got_2_lines == True
    
    def test_2_vertical_lines_are_not_detected_in_pattern(self):
        img = Image.open(os.path.join(settings.BASE_DIR, 'unit_test/broken_tests/test_data/mul95.jpg'))
        buf = 10  # buffer to include edge
        v_box = anly.BoxBorder(left=360-buf, upper=0, right=430+buf, lower=1080)
        ca = ContentAnalysis()
        got_2_lines = self.ca.count_vertical_lines(v_box, 2, img)
        
        assert got_2_lines == False

    def test_check_no_broken_pixel_inside_pattern(self):
        box = anly.BoxBorder(left=480, upper=0, right=560, lower=1920)
        # box = anly.BoxBorder(left=384, upper=0, right=448, lower=1536)
        images = ['unit_test/broken_tests/test_data/mul01.jpg', 'unit_test/broken_tests/test_data/mul02.jpg']

        for image in images:
            image = Image.open(os.path.join(settings.BASE_DIR, image))
            result = self.ca.check_no_broken_pixel(box , image)
            assert result == True

    def test_check_has_broken_pixels_inside_pattern(self):
        vbox = anly.BoxBorder(left=364, upper=0, right=414, lower=1080)
        images = ['unit_test/broken_tests/test_data/mul91.jpg', 'unit_test/broken_tests/test_data/mul92.jpg',
            'unit_test/broken_tests/test_data/mul93.jpg', 'unit_test/broken_tests/test_data/mul94.jpg',
            'unit_test/broken_tests/test_data/mul97.jpg']

        for image in images:
            image = Image.open(os.path.join(settings.BASE_DIR, image))
            result = self.ca.check_no_broken_pixel(vbox , image)
            assert result == False
        
        hbox = anly.BoxBorder(left=0, upper=273, right=1920, lower=313)
        images = [ 'unit_test/broken_tests/test_data/mul96.jpg' ]

        for image in images:
            image = Image.open(os.path.join(settings.BASE_DIR, image))
            result = self.ca.check_no_broken_pixel(hbox , image)
            assert result == False

    def test_cut_to_frames(self):
        self.ca.cut_to_frames(
            os.path.join(settings.BASE_DIR, 'unit_test/broken_tests/test_data/test02.mp4'),
            os.path.join(settings.BASE_DIR, 'unit_test/broken_tests/export'))

        assert os.path.isfile(os.path.join(settings.BASE_DIR, 'unit_test/broken_tests/export/mul00001.jpg'))
        shutil.rmtree(os.path.join(settings.BASE_DIR, 'unit_test/broken_tests/export/'))

    def test_trans_from_points_to_box(self):
        points = [480, 0, 560, 0, 560, 1919, 480, 1919]
        box = self.ca.trans_from_points_to_box(points)

        self.assertEqual(box, anly.BoxBorder(480, 0, 560, 1920))


    # def test_check_video_frames_as_usual_v2(self):
    #     privacy_mask_list = [ 
    #         anly.BoxBorder(left=384, upper=0, right=447, lower=1535),
    #         anly.BoxBorder(left=0, upper=1086, right=2047, lower=1153),
    #         anly.BoxBorder(left=0, upper=384, right=2047, lower=447),
    #         anly.BoxBorder(left=1598, upper=0, right=1665, lower=1535) ]
         
    #     is_usual = self.ca.check_video_frames_as_usual_v2(
    #         os.path.join( os.path.dirname( os.path.realpath( __file__ ) ), 'unittest/medium_stress' ),
    #         privacy_mask_list )
        
    #     self.assertEqual( is_usual, '{"message": "-", "analysis_result": "passed"}' )
    
    # def test_check_video_frames_as_usual_v3(self):
    #     privacy_mask_list = [ 
    #         anly.BoxBorder(left=384, upper=0, right=447, lower=1535),
    #         anly.BoxBorder(left=0, upper=1086, right=2047, lower=1153),
    #         anly.BoxBorder(left=0, upper=384, right=2047, lower=447),
    #         anly.BoxBorder(left=1598, upper=0, right=1665, lower=1535) ]
         
    #     result = self.ca.check_video_frames_as_usual_v3(
    #         os.path.join( os.path.dirname( os.path.realpath( __file__ ) ), 'unittest/medium_stress' ),
    #         privacy_mask_list
    #     )

    #     self.assertEqual( result, { 'result': 'passed', 'failed_frames': [] } )

    def test_check_video_frames_as_usual_v4(self):
        privacy_mask_list = [ 
            anly.BoxBorder(left=384, upper=0, right=447, lower=1535),
            anly.BoxBorder(left=0, upper=1086, right=2047, lower=1153),
            anly.BoxBorder(left=0, upper=384, right=2047, lower=447),
            anly.BoxBorder(left=1598, upper=0, right=1665, lower=1535) ]
        
        # Copy testing frames to dest
        jpg_files = ['seq1.jpg', 'seq2.jpg', 'seq3.jpg', 'seq4.jpg']
        tested_frames = map(lambda x: os.path.join( settings.BASE_DIR, 'unit_test/broken_tests/test_data', x), jpg_files)
        for filename in tested_frames:
            shutil.copy(filename, os.path.join( settings.BASE_DIR, 'unit_test/broken_tests/test_data/seq_frames' ))
        # Start check
        result = self.ca.check_video_frames_as_usual_v4(
            os.path.join( settings.BASE_DIR, 'unit_test/broken_tests/test_data/seq_frames' ),
            privacy_mask_list
        )

        self.assertEqual( result, { 'result': 'passed', 'failed_frames': [] } )

    # def test_save_snapshot_to_dir(self):
    #     framesFolderPath = '/home/dqa/data/pretests'
    #     roi = RoiModule('172.19.16.124', 'root', '', 'NAS')
    #     streamId = roi.get_recording_source()
    #     snapshot_path = self.ca('172.19.16.124', 'root', '').save_snapshot_to_dir(framesFolderPath, streamId)   
        
    #     self.assertEqual(
    #         os.path.exists(snapshot_path),
    #         True
    #     )
    #     self.assertGreater(
    #         os.path.getsize(snapshot_path),
    #         0
    #     )

    def tearDown(self):
        pass

if __name__ == "__main__":
    unittest.main()
