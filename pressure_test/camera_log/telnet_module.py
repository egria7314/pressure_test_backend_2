__author__ = "steven.hsiao"
import urllib
import base64

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

        # request = urllib.Request(url)
        req = urllib.request.Request(url)
        auth_str = username + ":" + password
        byteString = auth_str.encode(encoding="utf-8")
        encodestr = base64.b64encode(byteString)

        req.add_header("Authorization", "Basic %s" % encodestr.decode())

        try:
            # result = urllib.urlopen(request)
            result = urllib.request.urlopen(req)
        except Exception as e:
            # pass
            raise e
        else:
            return result