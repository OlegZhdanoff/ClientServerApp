from .log import configure_logging
from functools import wraps
import logging
import structlog
from logging.handlers import TimedRotatingFileHandler


def proc(logger, method_name, event_dict):
    # print("I got called with", event_dict)
    return repr(event_dict)


configure_logging(proc)


def log_config(logger_name, filename):
    logger = structlog.get_logger(logger_name)

    file_handler = TimedRotatingFileHandler(filename, when='D', interval=1, encoding='utf-8')
    logger.addHandler(file_handler)
    # logger.info('Тестовый запуск логгирования')
    return logger


def log_default(func):
    @wraps(func)
    def call(*args, **kwargs):
        return func(*args, **kwargs)
    return call