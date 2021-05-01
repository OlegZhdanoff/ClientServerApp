import time
from queue import Queue, Empty

from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.PublicKey import RSA

from GeekChat.log.log_config import log_config, log_default
from GeekChat.services import serializer, MSG_LEN_NAME, MSG_END_LEN_NAME
from GeekChat.messages import *

logger = log_config('client', 'client.log')


class Client:
    """
    class for process communication between client and server
    """
    def __init__(self, account_name, password, status='disconnected', sq_gui=None):
        """
        Constructor method
        :param account_name: user name
        :param password: plain user password
        :param status: user status
        :param sq_gui: Queue for communication with GUI
        """
        self.username = account_name
        self.password = password
        self.status = status
        self.data_queue = Queue()
        self.auth = False
        self.sq_gui = sq_gui

        key = RSA.generate(2048)
        self.public_key = key.publickey().export_key()
        self.private_key = key.export_key()
        self.session_key = None
        self.cipher_aes = None

    @log_default(logger)
    def __eq__(self, other):
        return self.username == other.username

    def __str__(self):
        return self.username

    @log_default(logger)
    def _set_status(self, status):
        self.status = status

    @log_default(logger)
    def feed_data(self, data):
        """
        send data to server
        Encrypt data if client has session_key and cipher
        :param data: Any type of @dataclass from .messages or `close`
        """
        if not data == 'close':
            if self.cipher_aes:
                data = self._encrypt_data(data)
            length = MSG_LEN_NAME + str(len(data)) + MSG_END_LEN_NAME
            data = length.encode() + data
        self.data_queue.put(data)

    # @log_default(logger)
    def get_data(self):
        """
        get data from user GUI
        """
        try:
            data = self.data_queue.get_nowait()
            self.data_queue.task_done()
            return data
        except Empty:
            pass

    @log_default(logger)
    def action_handler(self, msg):
        """
        process messages from server and client GUI
        :param msg: Any type of @dataclass from .messages
        """
        if isinstance(msg, Probe):
            self.feed_data(self.presence())
        # elif isinstance(msg, Msg):
        #     self.on_msg(msg)
        # elif isinstance(msg, Response):
        #     print(self.response_processor(msg))
        elif isinstance(msg, Authenticate):
            self.authenticated(msg)
        elif isinstance(msg, SendKey):
            self._set_session_key(msg)
        elif isinstance(msg, (GetContacts, FilterClients, Msg, Response)):
            if self.sq_gui:
                self.sq_gui.put(msg)
        else:
            print('action handler', msg)
            logger.warning(f"Unknown server's message {msg}")
            self.close()

    @log_default(logger)
    def response_processor(self, msg: Response):
        print(time.ctime(time.time()) + f': {msg.alert}')
        if msg.response in (200, 405, 409):
            return msg.alert
        if msg.response == 201:
            return msg.alert
        if msg.response == 203:
            return msg.alert
        elif msg.response == 202:
            return msg.alert
        elif msg.response == 402:
            return 'Your password is incorrect'
        elif msg.response == 404:
            return "User doesn't exist"
        else:
            logger.warning(f'Unknown response {msg}')
            return f'Unknown response {msg}'

    @log_default(logger)
    def _set_session_key(self, msg: SendKey):
        cipher_rsa = PKCS1_OAEP.new(RSA.import_key(self.private_key))
        self.session_key = cipher_rsa.decrypt(msg.key)
        self.cipher_aes = AES.new(self.session_key, AES.MODE_EAX)

        self.feed_data(self.authenticate())

    @log_default(logger)
    def _encrypt_data(self, data):
        self.cipher_aes = AES.new(self.session_key, AES.MODE_EAX)
        ciphertext, tag = self.cipher_aes.encrypt_and_digest(data)
        data = self.cipher_aes.nonce + tag + ciphertext
        return data

    @log_default(logger)
    @serializer
    def send_key(self):
        """
        send client public key to server
        """
        return SendKey(key=self.public_key)

    @log_default(logger)
    def authenticated(self, msg: Authenticate):
        """
        process Authenticate message from server
        send GetContacts message if Authenticate.result is True
        :param msg: Authenticate message from server
        :type msg: :class:`messages.Authenticate`
        """
        if msg.result:
            self.auth = True
            print('online')
            # self.status = 'online'
            self.feed_data(self.get_contacts())
        if self.sq_gui:
            self.sq_gui.put(msg)

    @log_default(logger)
    @serializer
    def authenticate(self):
        """
        send Authenticate request to server
        :return: :class:`messages.Authenticate`
        """
        return Authenticate(username=self.username, password=self.password)

    @log_default(logger)
    @serializer
    def get_contacts(self):
        """
        send GetContacts request to server
        :return: :class:`messages.GetContacts`
        """
        return GetContacts(login=self.username)

    @log_default(logger)
    @serializer
    def sender(self, msg):
        """
        send message to server
        :param msg: Any type of @dataclass from .messages
        """
        return msg

    @log_default(logger)
    @serializer
    def add_contact(self, name):
        """
        send AddContact request to server
        :param name: target username for adding to contact list
        :return: :class:`messages.AddContact`
        """
        return AddContact(username=name)

    @log_default(logger)
    @serializer
    def del_contact(self, name):
        """
        send DelContact request to server
        :param name: target username for deleting from contact list
        :return: :class:`messages.DelContact`
        """
        return DelContact(username=name)

    @log_default(logger)
    @serializer
    def _disconnect(self):
        """
        disconnect from server
        :return: :class:`messages.Quit`
        """
        return Quit()

    @log_default(logger)
    @serializer
    def presence(self):
        """
        send Presence answer to server
        :return: :class:`messages.Presence`
        """
        return Presence(username=self.username, status=self.status)

    @log_default(logger)
    @serializer
    def send_message(self, to, text):
        """
        send message to server to target user
        :param to: target username
        :param text: message body
        :return: :class:`messages.Msg`
        """
        return Msg(to=to, from_=self.username, text=text)

    @log_default(logger)
    @serializer
    def get_messages(self, tm, contact=''):
        """
        send GetMessages request to server
        :param tm: request messages created after this time
        :type tm: float
        :param contact: list of contacts returning by server
        :return: :class:`messages.GetMessages`
        """
        return GetMessages(time=tm, from_=contact)

    @log_default(logger)
    @serializer
    def join(self, room):
        """
        send Join request to server
        :param room: room name to join
        :return: :class:`messages.Join`
        """
        return Join(room=room)

    @log_default(logger)
    @serializer
    def leave(self, room):
        """
        send Leave request to server
        :param room: room name to leave
        :return: :class:`messages.Leave`
        """
        return Leave(room=room)

    @log_default(logger)
    def on_msg(self, msg):
        print(time.ctime(time.time()) + f': {msg.from_}: {msg.text}')

    @log_default(logger)
    def close(self):
        """
        close connection with server
        """
        if self.auth:
            self.auth = False
            self.feed_data(self._disconnect())
            time.sleep(0.5)
        self.feed_data('close')

    def _set_auth(self):
        self.auth = True
