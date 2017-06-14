# -*- coding: utf-8 -*-
"""This telnet module connect server and client by telnet login.

.. module:: telnet.
   :synopsis: A simple module for connecting server

.. moduleauthor:: carlos.hu

"""


__author__ = 'carlos.hu'
import telnetlib
import urllib.request
import base64


class URI(object):
    """This class build connection between server and client."""

    @staticmethod
    def set(url, username="root", password=""):
        """
        Set URI's content.

        Args:
        url : The string of url that is url command.
        username: The string of username that is camera account.
        password: The string of password that is camera password.

        Returns:
            string. Server feedback.
        """
        request = urllib.request.Request(url)
        print (request)
        print ('checkpoint00')
        base64string = base64.encodestring(('%s:%s' % (username,password)).encode()).decode().replace('\n', '')

        print (base64string)
        request.add_header("Authorization", "Basic %s" % base64string)
        try:
            print ('checkpoin11')
            result = urllib.request.urlopen(request)
        except Exception as e:
            raise e
        else:
            print ('result = {0}'.format(result))
            return result


class TelnetModule(object):
    """This function build connection between server and client machine."""

    def __init__(self, ip, account, password):
        """
        TelnetModule initialize.

        Args:
          ip (str) : The string of ip that is camera ip.
          username (str): The string of username that is camera account.
          password (str): The string of password that is camera password.

        """
        self.ip = ip
        self.account = account
        self.password = password
        #open camera telnet
        URI.set('http://' + self.ip + '/cgi-bin/admin/mod_inetd.cgi?telnet=on', self.account, self.password)
        self.tn = telnetlib.Telnet(self.ip, "", 5)
        self.data = []

    def login(self):
        """Login machine."""
        tn = self.tn
        tn.read_until("login: ")
        tn.write(self.account + "\n")

        password_check = tn.read_until("Password: ", 5)
        #confirm console display password input box
        if 'Password' in password_check:
            tn.write(self.password + "\n")
            tn.read_until("~ #", 5)
        else:
            pass
        return self

    def send_command(self, commands):
        """
        Send commands.

        Args:
        commands : The string of commands that is url command.
        """
        tn = self.tn
        tn.write(str(commands)+"\n")
        self.data.append(tn.read_until("~ #", 3000))
        return self

    def result(self):
        """
        Return the result.

        Returns:
            string. Server feedback.
        """
        return self.data