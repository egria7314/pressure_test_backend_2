import logging
import logging.config
import os


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

    @staticmethod
    def logging_debug(debug):
        PressureTestLogging.logger.debug(debug)

    @staticmethod
    def logging_info(info):
        PressureTestLogging.logger.info(info)

    @staticmethod
    def logging_warning(warning):
        PressureTestLogging.logger.warning(warning)

    @staticmethod
    def logging_error(error):
        PressureTestLogging.logger.error(error)

    @staticmethod
    def logging_critical(critical):
        PressureTestLogging.logger.critical(critical)


def main():
    PressureTestLogging.logging_debug('pressure test had a debug log')
    PressureTestLogging.logging_info('pressure test had a info log')
    PressureTestLogging.logging_warning('pressure test had a warning log')
    PressureTestLogging.logging_error('pressure test had a error log')
    PressureTestLogging.logging_critical('pressure test had a critical log')


if __name__ == '__main__':
    main()