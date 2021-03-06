from time import sleep, time
import sys, threading


class KThread(threading.Thread):
    """A subclass of threading.Thread, with a kill()

    method.

    Come from:

    Kill a thread in Python:

    http://mail.python.org/pipermail/python-list/2004-May/260937.html

    """

    def __init__(self, *args, **kwargs):

        threading.Thread.__init__(self, *args, **kwargs)

        self.killed = False

    def start(self):

        """Start the thread."""

        self.__run_backup = self.run

        self.run = self.__run  # Force the Thread to install our trace.

        threading.Thread.start(self)

    def __run(self):

        """Hacked run function, which installs the

        trace."""

        sys.settrace(self.globaltrace)

        self.__run_backup()

        self.run = self.__run_backup

    def globaltrace(self, frame, why, arg):

        if why == 'call':

            return self.localtrace

        else:

            return None

    def localtrace(self, frame, why, arg):

        if self.killed:

            if why == 'line':
                raise SystemExit()

        return self.localtrace

    def kill(self):

        self.killed = True


class Timeout(Exception):
    """function run timeout"""


def timeout(seconds):


    def timeout_decorator(func):


        def _new_func(oldfunc, result, oldfunc_args, oldfunc_kwargs):

            result.append(oldfunc(*oldfunc_args, **oldfunc_kwargs))

        def _(*args, **kwargs):

            result = []

            new_kwargs = {  # create new args for _new_func, because we want to get the func return val to result list

                'oldfunc': func,

                'result': result,

                'oldfunc_args': args,

                'oldfunc_kwargs': kwargs

            }

            thd = KThread(target=_new_func, args=(), kwargs=new_kwargs)

            thd.start()

            thd.join(seconds)

            alive = thd.isAlive()

            thd.kill()  # kill the child thread

            if alive:
                # raise Timeout(u'function run too long, timeout %d seconds.' % seconds)
                try:

                    raise Timeout(u'function run too long, timeout %d seconds.' % seconds)
                finally:
                    return u'function run too long, timeout %d seconds.' % seconds

            else:

                return result[0]

        _.__name__ = func.__name__

        _.__doc__ = func.__doc__

        return _

    return timeout_decorator

# from functools import wraps
# import errno
# import os
# import signal
#
# class TimeoutError(Exception):
#     pass
#
# def timeout(seconds=5, error_message=os.strerror(errno.ETIME)):
#     def decorator(func):
#         def _handle_timeout(signum, frame):
#             raise TimeoutError(error_message)
#
#         def wrapper(*args, **kwargs):
#             signal.signal(signal.SIGALRM, _handle_timeout)
#             signal.alarm(seconds)
#             try:
#                 result = func(*args, **kwargs)
#             finally:
#                 signal.alarm(0)
#             return result
#
#         return wraps(func)(wrapper)
#
#     return decorator