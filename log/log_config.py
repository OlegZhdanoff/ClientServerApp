from .log import configure_logging
from functools import wraps
import structlog
from logging.handlers import TimedRotatingFileHandler
import inspect


def proc(logger, method_name, event_dict):
    return event_dict


configure_logging(proc)


def log_config(logger_name, filename):
    logger = structlog.get_logger(logger_name)

    file_handler = TimedRotatingFileHandler(filename, when='D', interval=1, encoding='utf-8')
    logger.addHandler(file_handler)
    return logger


def log_default(logger):
    def decorator(func):
        @wraps(func)
        def call(*args, **kwargs):
            args_str = ', '.join([str(arg) for arg in args[1:]])
            logger.info(f'function {func.__name__}({args_str}) called from {inspect.stack()[1].function}')
            return func(*args, **kwargs)
        return call
    return decorator
