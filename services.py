import errno
import time
import json
import queue
from dataclasses import dataclass
from functools import wraps
import socket
from json import JSONDecodeError

from log.log_config import log_config, log_default

ENCODING = 'utf-8'
MAX_MSG_SIZE = 640

DEFAULT_SERVER_IP = 'localhost'
DEFAULT_SERVER_PORT = 7777

MSG_LEN_NAME = 'msg_len='

logger = log_config('services', 'services.log')


class SelectableQueue(queue.Queue):
    def __init__(self, put_socket, get_socket, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._put_socket = put_socket
        self._get_socket = get_socket

    def fileno(self):
        return self._get_socket.fileno()

    def getpeername(self):
        return self._get_socket.getpeername()

    def put(self, item, *args, **kwargs):
        super().put(item, *args, **kwargs)
        self._put_socket.send(b'x')
        # print('put')

    def get(self, *args, **kwargs):
        self._get_socket.recv(1)
        return super().get()

    def is_not_empty(self):
        return not super().empty()

    def close(self):
        self._get_socket.close()
        self._put_socket.close()


def serializer(func):
    @wraps(func)
    def inner(*args, **kwargs):
        res = json.dumps(func(*args, **kwargs))
        return ('msg_len=' + str(len(res)) + res).encode(ENCODING)
    return inner


class MessagesDeserializer:

    @classmethod
    @log_default(logger)
    def get_messages(cls, conn):
        data = cls.recv_all(conn)
        return cls.get_msg_list(data)

    @staticmethod
    def recv_all(conn):
        data = b''
        if isinstance(conn, SelectableQueue):
            data = conn.get()
            conn.task_done()
            return data.decode(ENCODING) if data else None

        try:
            while True:
                old_data = data
                data += conn.recv(MAX_MSG_SIZE)
                if data == old_data:
                    return data.decode(ENCODING)
        except socket.error as exc:
            return data.decode(ENCODING)
        except Exception as e:
            return data.decode(ENCODING)

    @classmethod
    def get_msg_list(cls, data):
        res = []
        while data:
            length, end_length = cls.get_msg_lengths(data)
            if length and len(data) >= (end_length + length):
                res.append(
                    cls.deserialize(data[end_length:end_length + length])
                )
                data = data[end_length + length:]
        return res

    @staticmethod
    def get_msg_lengths(data):
        start_length = data.find(MSG_LEN_NAME) + len(MSG_LEN_NAME)
        end_length = data.find('{', start_length)
        length = data[start_length:end_length]
        return (int(length), end_length) if length.isdigit() else (False, False)

    @staticmethod
    def deserialize(data):
        try:
            return json.loads(data)
        except JSONDecodeError as e:
            logger.exception(f'Disconnect! JSONDecodeError for data: {data}')
            return ''
        except TypeError as e:
            logger.exception(f'Disconnect! Wrong type of data: {data}')
            return ''


class MessageProcessor:
    pass


@dataclass
class Presence:
    user: dict
    action: str = 'presence'
    time: float = time.time()
    type: str = 'status'


