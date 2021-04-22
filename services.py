import base64
import configparser
import json
import pickle
import queue
from functools import wraps
import socket
from json import JSONDecodeError
from pathlib import Path

from Crypto.Cipher import AES
from icecream import ic

from log.log_config import log_config, log_default
from messages import *

ENCODING = 'utf-8'
MAX_MSG_SIZE = 1024

DEFAULT_SERVER_IP = 'localhost'
DEFAULT_SERVER_PORT = 7777
DEFAULT_DB = 'sqlite:///chat.db'
LOCAL_ADMIN = 'local_admin'
LOCAL_ADMIN_PASSWORD = '123'
PING_INTERVAL = 200

MSG_LEN_NAME = 'msg_len='
MSG_END_LEN_NAME = 'length_end'

logger = log_config('services', 'services.log')


STATUS = ('online', 'disconnected', 'afk', 'busy')


class Config:
    def __init__(self, path: Path):
        if not path.exists():
            logger.warning(f"config file {path} does't exists")
            raise OSError(f"config file {path} does't exists")
        self.path = path
        self.data = configparser.ConfigParser()
        self.load_config()

    def load_config(self):
        self.data.read(self.path)

    def save_config(self):
        with open(self.path, 'w', encoding=ENCODING) as f:
            self.data.write(f)


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
            # ic(obj)
            return obj.__json__()
        if isinstance(obj, bytes):
            return base64.b64encode(obj, altchars=None).decode()
        #     return {"key": obj}
        print('class MessageEncoder: obj -> ', obj)
        return json.JSONEncoder.default(self, obj)


def serializer(func):
    @wraps(func)
    def inner(*args, **kwargs):
        # ic(*args)
        # ic(**kwargs)
        # ic(func)
        # res = json.dumps(func(*args, **kwargs), cls=MessageEncoder)
        res = pickle.dumps(func(*args, **kwargs))
        # length = pickle.dumps('msg_len=' + str(len(res)))
        return res
    return inner


class MessagesDeserializer:
    session_key = None

    @classmethod
    @log_default(logger)
    def get_messages(cls, conn, session_key=None):
        data = cls.recv_all(conn)
        cls.session_key = session_key
        if data:
            # print('======== get messages =========')
            # ic(data)
            # ic(session_key)
            # ic(pickle.loads(data))
            # if session_key:
            #     data = cls.decrypt(data)
            # ic(data)
            res = cls.get_msg_list(data)
            # ic(res)
            # res = pickle.loads(data)
            # ic('MessagesDeserializer get_messages ', res)
            return res

    @staticmethod
    def recv_all(conn):
        data = b''
        # ic(conn)
        if isinstance(conn, SelectableQueue):
            data = conn.get()
            conn.task_done()
            # return data.decode(ENCODING) if data else None
            return data

        try:
            while True:
                old_data = data
                data += conn.recv(MAX_MSG_SIZE)
                if data == old_data:
                    return data
        except socket.error as exc:
            print('socket.error', exc)
            return data
        except Exception as e:
            print('Exception', e)
            return data

    @classmethod
    def decrypt(cls, data):
        # enc_session_key, nonce, tag, ciphertext = \
        #     [file_in.read(x) for x in (private_key.size_in_bytes(), 16, 16, -1)]

        # Decrypt the data with the AES session key

        # print(data.decode("utf-8"))
        try:
            nonce = data[:16]
            tag = data[16:32]
            ciphertext = data[32:]
            # print('========= decrypt ================')
            # ic(nonce)
            # ic(tag)
            # ic(ciphertext)
            # ic(cls.session_key)
            cipher_aes = AES.new(cls.session_key, AES.MODE_EAX, nonce)
            data = cipher_aes.decrypt_and_verify(ciphertext, tag)
            # ic(data)
        except Exception as e:
            ic(f"decrypt error  {e}")
            logger.exception(f"decrypt error  {e}")
        return data

    @classmethod
    def get_msg_list(cls, data):
        res = []
        while data:
            # ic(data)
            length, end_length = cls.get_msg_lengths(data)
            if length and len(data) >= (end_length + length):
                current_data = data[end_length:end_length + length]

                if cls.session_key:
                    current_data = cls.decrypt(current_data)

                res.append(
                    cls.deserialize(current_data)
                )
                data = data[end_length + length:]
        return res

    @staticmethod
    def get_msg_lengths(data):
        start_length = data.find(MSG_LEN_NAME.encode()) + len(MSG_LEN_NAME)
        end_length = data.find(MSG_END_LEN_NAME.encode(), start_length)
        length = data[start_length:end_length]
        end_length += len(MSG_END_LEN_NAME)
        return (int(length), end_length) if length.isdigit() else (False, False)

    @staticmethod
    def deserialize(data):
        try:
            return pickle.loads(data)
        except pickle.UnpicklingError as e:
        # except JSONDecodeError as e:
        #     logger.exception(f'Disconnect! JSONDecodeError for data: {data}')
            logger.exception(f'UnpicklingError for data: {data}')
            return ''
        except TypeError as e:
            logger.exception(f'Wrong type of data: {data}')
            return ''


class MessageProcessor:
    @staticmethod
    def from_msg(msg):
        if "action" in msg:
            if msg['action'] == 'presence':
                return Presence(
                    action=msg['action'],
                    time=msg['time'],
                    type=msg['type'],
                    username=msg['user']['account_name'],
                    status=msg['user']['status']
                )
            elif msg['action'] == 'authenticate':
                return Authenticate(
                    action=msg['action'],
                    time=msg['time'],
                    username=msg['user']['account_name'],
                    password=msg['user']['password'],
                    result=msg['result'],
                    alert=msg['alert']
                )
            elif msg['action'] == 'quit':
                return Quit()
            elif msg['action'] == 'probe':
                return Probe(
                    action=msg['action'],
                    time=msg['time'],
                )
            elif msg['action'] == 'msg':
                return Msg(
                    action=msg['action'],
                    time=msg['time'],
                    to=msg['to'],
                    from_=msg['from'],
                    text=msg['message']
                )
            elif msg['action'] == 'get_messages':
                return GetMessages(
                    action=msg['action'],
                    time=msg['time'],
                    from_=msg['from_'],
                )
            elif msg['action'] == 'join':
                return Join(
                    action=msg['action'],
                    time=msg['time'],
                    room=msg['room'],
                )
            elif msg['action'] == 'leave':
                return Leave(
                    action=msg['action'],
                    time=msg['time'],
                    room=msg['room'],
                )
            elif msg['action'] == 'get_contacts':
                return GetContacts(
                    action=msg['action'],
                    time=msg['time'],
                    contacts=msg['contacts'],
                    login=msg['login']
                )
            elif msg['action'] == 'add_contact':
                return AddContact(
                    action=msg['action'],
                    time=msg['time'],
                    username=msg['username'],
                )
            elif msg['action'] == 'del_contact':
                return DelContact(
                    action=msg['action'],
                    time=msg['time'],
                    username=msg['username'],
                )
            elif msg['action'] == 'filter_clients':
                return FilterClients(
                    action=msg['action'],
                    time=msg['time'],
                    pattern=msg['filter'],
                    users=msg['users'],
                )
            elif msg['action'] == 'public_key':
                return SendKey(
                    action=msg['action'],
                    key=msg['key'],
                )
        elif "response" in msg:
            return Response(
                response=msg['response'],
                time=msg['time'],
                alert=msg['alert']
            )
