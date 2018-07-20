"""This module consist methods for logs"""
import logging
import os


class LoggerUtils:
    """Class for Logger utility."""
    @staticmethod
    def setLevel():
        """Method for setLevel"""
        logFormat = '%(asctime)-15s %(levelname)s:%(message)s'
        logging.basicConfig(format=logFormat)
        logger = logging.getLogger("utility-logger")

        try:
            logLevel = os.environ["logLevel"]
        except Exception as e:
            logLevel = "INFO"

        logger.setLevel(logging.getLevelName(logLevel))
        return True

    @staticmethod
    def info(message):
        """Method to print info logs"""
        logger = logging.getLogger("utility-logger")
        logger.info('%s', message)
        return True

    @staticmethod
    def error(message):
        """Method to print error logs"""
        logger = logging.getLogger("utility-logger")
        logger.error('%s', message)
        return True

    @staticmethod
    def warn(message):
        """Method to print warning logs"""
        logger = logging.getLogger("utility-logger")
        logger.warning('%s', message)
        return True

    @staticmethod
    def debug(message):
        """Method to print debug logs"""
        logger = logging.getLogger("utility-logger")
        logger.debug('%s', message)
        return True

