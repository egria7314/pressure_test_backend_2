# -*- coding: utf-8 -*-
import unittest
from broken_tests.helpers.http_module import URI


class TestHttpModule(unittest.TestCase):
    def setUp(self):
        self.ip = '172.19.16.124'
        self.account = 'root'
        self.password = '123'


    # def test_set(self):
    #     response = URI.set('http://172.19.16.124/cgi-bin/admin/mod_inetd.cgi?telnet=on',self.account,self.password)
    #     print( response.read() )


    def tearDown(self):
        pass


if __name__ == "__main__":
    unittest.main()