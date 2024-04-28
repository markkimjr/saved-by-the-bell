import logging
import settings

LOGGER_NAME = "sbtb"


class Logger:
    _instance = None

    def __init__(self, log_level=logging.INFO):
        self.logger = logging.getLogger(LOGGER_NAME)
        self.logger.setLevel(log_level)
        formatter = logging.Formatter(
            fmt='%(asctime)s - %(levelname)s - %(filename)s:%(funcName)s:%(lineno)d - %(message)s',
            datefmt='%m/%d/%Y %I:%M:%S')
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        self.logger.addHandler(stream_handler)

    def get_logger(self):
        return self.logger

    # singleton approach to use only one instance of Logger throughout project
    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = cls(log_level=settings.log_level).get_logger()
        return cls._instance

    def info(self, msg):
        self.logger.info(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)

    def critical(self, msg):
        self.logger.critical(msg)
