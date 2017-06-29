__author__ = "steven.hsiao"
# import urllib
import base64

import telnetlib
import urllib.request


class URI(object):
    """This class build connection between server and client."""

    @staticmethod
    def set(url, username="root", password="", timeout=300):
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
            result = urllib.request.urlopen(req, timeout=timeout)
        except Exception as e:
            # pass
            raise e
        else:
            return result


class TelnetModule(object):
    """This function build connection between server and client machine."""

    def __init__(self, ip, account, password, timeout=300):
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
        URI.set('http://' + self.ip + '/cgi-bin/admin/mod_inetd.cgi?telnet=on', self.account, self.password, timeout)
        self.tn = telnetlib.Telnet(self.ip, "", 5)
        self.data = []

    def login(self):
        """Login machine."""
        tn = self.tn
        tn.read_until(b"login: ")
        tn.write(self.account.encode(encoding="utf-8") + b"\n")
        password_check = tn.read_until(b"Password: ", 5)
        #confirm console display password input box
        if b'Password' in password_check:
            tn.write(self.password.encode(encoding="utf-8") + b"\n")
            tn.read_until(b"~ #", 5)
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
        tn.write(str(commands).encode(encoding="utf-8") + b"\n")
        self.data.append(tn.read_until(b"~ #", 3000))           # wait very long     # TODO
        return self

    def result(self):
        """
        Return the result.

        Returns:
            string. Server feedback.
        """
        return self.data