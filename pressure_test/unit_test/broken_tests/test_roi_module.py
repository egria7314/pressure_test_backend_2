# -*- coding: utf-8 -*-
import unittest
from broken_tests.helpers.roi_module import RoiModule


class TestRoiModule(unittest.TestCase):
    def setUp(self):
        self.ip = '172.19.16.124'
        self.account = 'root'
        self.password = '123'
        self.destination = 'NAS'


    # def test_return_mask(self):
    #     roi = RoiModule(self.ip, self.account, self.password, self.destination)
    #     print(roi.return_mask())
    #     assert True

    # def test_get_mask_position(self):
    #     roi = RoiModule(self.ip, self.account, self.password, self.destination)
    #     print( roi.get_mask_position() )

    def tearDown(self):
        pass


if __name__ == "__main__":
    unittest.main()