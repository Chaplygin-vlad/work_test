import logging
import os
import sys
from logging.handlers import TimedRotatingFileHandler


class LogDispatcher:
    def __init__(self, logger_name='MAIN'):
        self.logging_level = 'INFO'
        self.logging_to_console = True
        self.logs_dir = 'logs'
        os.makedirs(self.logs_dir, exist_ok=True)
        self.log_file = self.logs_dir + '/' + logger_name + '.log'
        self.log_format_stream = logging.Formatter('[%(asctime)s] -%(levelname)s'
                                                   ' %(module)s::%(funcName)s():l%(lineno)d: %(message)s')
        self.log_format_file = self.log_format_stream
        self.log = self.__get_logger(logger_name)

    def __get_console_handler(self):
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(self.log_format_stream)
        return console_handler

    def __get_file_handler(self):
        file_handler = TimedRotatingFileHandler(self.log_file, when='midnight')
        file_handler.setFormatter(self.log_format_file)
        return file_handler

    def __get_logger(self, logger_name):
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.getLevelName(self.logging_level))
        if len(logger.handlers) == 0:
            if self.logging_to_console:
                logger.addHandler(self.__get_console_handler())
            if self.logs_dir != '':
                logger.addHandler(self.__get_file_handler())
        logger.propagate = False
        return logger
