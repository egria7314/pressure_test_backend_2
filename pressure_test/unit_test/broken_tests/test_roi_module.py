# -*- coding: utf-8 -*-
import unittest
from broken_tests.helpers.roi_module import RoiModule
from broken_tests import views


class TestRoiModule(unittest.TestCase):
    def setUp(self):
        self.ip = '172.19.1.50'
        self.account = 'root'
        self.password = '12345678z'
        self.destination = 'NAS'


    # def test_return_mask(self):
    #     roi = RoiModule(self.ip, self.account, self.password, self.destination)
    #     print(roi.return_mask())
    #     assert True

    # def test_get_mask_position(self):
    #     roi = RoiModule(self.ip, self.account, self.password, self.destination)
    #     print( roi.mask_position_dict )
    #     assert True
    
    # def test_module_pretest_broken_image(self):
    #     result = views.module_pretest_broken_image(self.ip, self.account, self.password, self.destination)
    #     print(result)
    #     print(type(result))
    #     assert isinstance(result, dict)
    #     assert result['result'] == 'passed'

    def tearDown(self):
        pass


if __name__ == "__main__":
    unittest.main()