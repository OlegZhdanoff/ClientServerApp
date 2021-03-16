import errno
import json
from functools import wraps
import socket

ENCODING = 'utf-8'
MAX_MSG_SIZE = 640

DEFAULT_SERVER_IP = 'localhost'
DEFAULT_SERVER_PORT = 7777

MSG_LEN_NAME = 'msg_len='


def send_json(func):
    @wraps(func)
    def inner(*args, **kwargs):
        res = json.dumps(func(*args, **kwargs))
        return ('msg_len=' + str(len(res)) + res).encode(ENCODING)
    return inner


def recv_all(conn):
    data = ''
    try:
        while True:
            data += conn.recv(MAX_MSG_SIZE).decode(ENCODING)
    except socket.error as exc:
        err = exc.args[0]
        if err in (errno.EAGAIN, errno.EWOULDBLOCK):

            return data


def get_msg_list(data):
    res = []
    while len(data):
        length, end_length = get_msg_lengths(data)
        if length and len(data) >= (end_length + length):
            res.append(data[end_length:end_length + length])
            print('data = ', data)
            print(res)
            data = data[end_length + length:]
            print('data new = ', data)
    return res


def get_msg_lengths(data):
    start_length = data.find(MSG_LEN_NAME) + len(MSG_LEN_NAME)
    end_length = data.find('{', start_length)
    length = data[start_length:end_length]
    return (int(length), end_length) if length.isdigit() else (False, False)