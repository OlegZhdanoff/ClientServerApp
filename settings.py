import json
from functools import wraps

ENCODING = 'utf-8'
MAX_MSG_SIZE = 640

DEFAULT_SERVER_IP = 'localhost'
DEFAULT_SERVER_PORT = 7777


def send_json(func):
    @wraps(func)
    def inner(*args, **kwargs):
        return json.dumps(func(*args, **kwargs)).encode(ENCODING)
    return inner
