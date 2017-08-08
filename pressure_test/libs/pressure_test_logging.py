import logging
import logging.config
import os
import inspect


class PressureTestLogging(object):
  
    # Create log folder
    # if not os.path.exists(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))) + '/log')):
    #     os.mkdir(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))) + '/log'))
    if not os.path.join(os.path.dirname(__file__), 'log'):
      os.mkdir('log')
    print (os.path.join(os.path.dirname(__file__), 'log'))
    LOGGER_NAME = 'pt_log'
    LOGGER_FILENAME = os.path.join(os.path.dirname(__file__), 'logging.conf')
    print (LOGGER_FILENAME)
    logging.config.fileConfig(LOGGER_FILENAME)
    logger = logging.getLogger(LOGGER_NAME)
    projectName = "PressureTest"

    @staticmethod
    def getmodule():
        frame = inspect.stack()[2]
        module = inspect.getmodule(frame[0])
        return module.__name__

    @staticmethod
    def logging_debug(debug):
        caller = PressureTestLogging.getmodule()
        PressureTestLogging.logger.debug("[{0}][{1}][{2}]".format(PressureTestLogging.projectName, caller, debug))

    @staticmethod
    def logging_info(info):
        caller = PressureTestLogging.getmodule()
        PressureTestLogging.logger.info("[{0}][{1}][{2}]".format(PressureTestLogging.projectName, caller, info))

    @staticmethod
    def logging_warning(warning):
        caller = PressureTestLogging.getmodule()
        PressureTestLogging.logger.warning("[{0}][{1}][{2}]".format(PressureTestLogging.projectName, caller, warning))

    @staticmethod
    def logging_error(error):
        caller = PressureTestLogging.getmodule()
        PressureTestLogging.logger.error("[{0}][{1}][{2}]".format(PressureTestLogging.projectName, caller, error))

    @staticmethod
    def logging_critical(critical):
        caller = PressureTestLogging.getmodule()
        PressureTestLogging.logger.critical("[{0}][{1}][{2}]".format(PressureTestLogging.projectName, caller, critical))


def main():
    PressureTestLogging.logging_debug('pressure test had a debug log')
    PressureTestLogging.logging_info('pressure test had a info log')
    PressureTestLogging.logging_warning('pressure test had a warning log')
    PressureTestLogging.logging_error('pressure test had a error log')
    PressureTestLogging.logging_critical('pressure test had a critical log')


if __name__ == '__main__':
    main()