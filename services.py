import json
import queue
from functools import wraps
import socket
from json import JSONDecodeError

from log.log_config import log_config, log_default
from messages import *

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


class MessageEncoder(json.JSONEncoder):
    """
    JSONEncoder subclass that leverages an object's `__json__()` method,
    if available, to obtain its default JSON representation.

    """
    def default(self, obj):
        if hasattr(obj, '__json__'):
            return obj.__json__()
        return json.JSONEncoder.default(self, obj)


def serializer(func):
    @wraps(func)
    def inner(*args, **kwargs):
        res = json.dumps(func(*args, **kwargs), cls=MessageEncoder)
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
    @staticmethod
    def from_msg(msg):
        if "action" in msg:
            if msg['action'] == 'presence':
                return Presence(
                    action='presence',
                    time=msg['time'],
                    type=msg['type'],
                    username=msg['user']['account_name'],
                    status=msg['user']['status']
                )
            if msg['action'] == 'authenticate':
                return Authenticate(
                    action='authenticate',
                    time=msg['time'],
                    username=msg['user']['account_name'],
                    password=msg['user']['password']
                )
            if msg['action'] == 'quit':
                return Quit()
            if msg['action'] == 'probe':
                return Probe(
                    action='probe',
                    time=msg['time'],
                )
            if msg['action'] == 'msg':
                return Msg(
                    action='msg',
                    time=msg['time'],
                    to=msg['to'],
                    from_=msg['from'],
                    text=msg['message']
                )
            if msg['action'] == 'join':
                return Join(
                    action='join',
                    time=msg['time'],
                    room=msg['room'],
                )
            if msg['action'] == 'leave':
                return Leave(
                    action='leave',
                    time=msg['time'],
                    room=msg['room'],
                )
        elif "response" in msg:
            return Response(
                response=msg['response'],
                time=msg['time'],
                alert=msg['alert']
            )