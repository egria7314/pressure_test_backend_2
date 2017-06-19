# -*- coding: utf-8 -*-
import urllib.request


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
        p = urllib.request.HTTPPasswordMgrWithDefaultRealm()
        p.add_password(realm=None, uri=url, user=username, passwd=password)
        auth_handler = urllib.request.HTTPBasicAuthHandler(p)
        opener = urllib.request.build_opener(auth_handler)
        # ...and install it globally so it can be used with urlopen.
        urllib.request.install_opener(opener)
        
        try:
            result = urllib.request.urlopen(url)
        except Exception as e:
            raise e
        else:
            return result
