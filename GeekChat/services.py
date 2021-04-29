import base64
import configparser
import json
import pickle
import queue
from functools import wraps
import socket
from pathlib import Path

from Crypto.Cipher import AES
from icecream import ic

from GeekChat.log.log_config import log_config, log_default
from .messages import *

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
        """
        create ConfigParser object for specific configuration file
        :param path: path to configuration file
        """
        if not path.exists():
            logger.warning(f"config file {path} does't exists")
            raise OSError(f"config file {path} does't exists")
        self.path = path
        self.data = configparser.ConfigParser()
        self.load_config()

    def load_config(self):
        """
        load data from configuration file
        """
        self.data.read(self.path)

    def save_config(self):
        """
        save data to configuration file
        :return:
        """
        with open(self.path, 'w', encoding=ENCODING) as f:
            self.data.write(f)


class SelectableQueue(queue.Queue):

    def __init__(self, put_socket, get_socket, *args, **kwargs):
        """
        specific Queue, worked with selectors
        :param put_socket: socket for put method
        :param get_socket: socket for get method
        """
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
        print('class MessageEncoder: obj -> ', obj)
        return json.JSONEncoder.default(self, obj)


def serializer(func):
    @wraps(func)
    def inner(*args, **kwargs):
        res = pickle.dumps(func(*args, **kwargs))
        return res

    return inner


class MessagesDeserializer:
    """
    class for deserialize all types of @dataclass from .messages
    """
    session_key = None

    @classmethod
    @log_default(logger)
    def get_messages(cls, conn, session_key=None):
        """
        get messages from socket
        :param conn: socket
        :param session_key: session key for decrypt messages
        :return: messages @dataclass from .messages
        """
        data = cls.recv_all(conn)
        cls.session_key = session_key
        if data:
            res = cls.get_msg_list(data)
            return res

    @staticmethod
    def recv_all(conn):
        """
        read data from socket
        :param conn: socket
        :return: data from socket
        """
        data = b''
        if isinstance(conn, SelectableQueue):
            data = conn.get()
            conn.task_done()
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
        """
        Decrypt the data with the AES session key
        :param data: received data from socket
        :return: decrypted data
        """
        try:
            nonce = data[:16]
            tag = data[16:32]
            ciphertext = data[32:]
            cipher_aes = AES.new(cls.session_key, AES.MODE_EAX, nonce)
            data = cipher_aes.decrypt_and_verify(ciphertext, tag)
        except Exception as e:
            ic(f"decrypt error  {e}")
            logger.exception(f"decrypt error  {e}")
        return data

    @classmethod
    def get_msg_list(cls, data):
        """
        process received data to separated messages list
        :param data: received data from socket
        :return: list of messages @dataclass from .messages
        """
        res = []
        while data:
            length, end_length = cls._get_msg_lengths(data)
            if length and len(data) >= (end_length + length):
                current_data = data[end_length:end_length + length]

                if cls.session_key:
                    current_data = cls.decrypt(current_data)

                res.append(
                    cls._deserialize(current_data)
                )
                data = data[end_length + length:]
        return res

    @staticmethod
    def _get_msg_lengths(data):
        start_length = data.find(MSG_LEN_NAME.encode()) + len(MSG_LEN_NAME)
        end_length = data.find(MSG_END_LEN_NAME.encode(), start_length)
        length = data[start_length:end_length]
        end_length += len(MSG_END_LEN_NAME)
        return (int(length), end_length) if length.isdigit() else (False, False)

    @staticmethod
    def _deserialize(data):
        try:
            return pickle.loads(data)
        except pickle.UnpicklingError:
            # except JSONDecodeError as e:
            #     logger.exception(f'Disconnect! JSONDecodeError for data: {data}')
            logger.exception(f'UnpicklingError for data: {data}')
            return ''
        except TypeError:
            logger.exception(f'Wrong type of data: {data}')
            return ''


class MessageProcessor:
    """
    creat messages @dataclass from .messages from json data
    """
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
