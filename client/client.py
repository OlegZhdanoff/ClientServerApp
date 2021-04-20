import pickle
import time
from queue import Queue, Empty

from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.PublicKey import RSA

import structlog
from icecream import ic

from log.log_config import log_config, log_default
from services import serializer
from messages import *

logger = log_config('client', 'client.log')


class Client:
    def __init__(self, account_name, password, status='disconnected', sq_gui=None):
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
    def set_status(self, status):
        self.status = status

    @log_default(logger)
    def feed_data(self, data):
        if self.cipher_aes:
            self.data_queue.put(self.encrypt_data(data))
        else:
            self.data_queue.put(data)

    # @log_default(logger)
    def get_data(self):
        try:
            data = self.data_queue.get_nowait()
            self.data_queue.task_done()
            return data
        except Empty as e:
            pass

    @log_default(logger)
    def action_handler(self, msg):
        if isinstance(msg, Probe):
            self.feed_data(self.presence())
        # elif isinstance(msg, Msg):
        #     self.on_msg(msg)
        elif isinstance(msg, Response):
            print(self.response_processor(msg))
        elif isinstance(msg, Authenticate):
            self.authenticated(msg)
        elif isinstance(msg, SendKey):
            self.set_session_key(msg)
        elif isinstance(msg, (GetContacts, FilterClients, Msg)):
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
    def set_session_key(self, msg: SendKey):
        cipher_rsa = PKCS1_OAEP.new(RSA.import_key(self.private_key))
        self.session_key = cipher_rsa.decrypt(msg.key)
        self.cipher_aes = AES.new(self.session_key, AES.MODE_EAX)

        self.feed_data(self.authenticate())

    @log_default(logger)
    def encrypt_data(self, data):
        # Encrypt the data with the AES session key
        ciphertext, tag = self.cipher_aes.encrypt_and_digest(data)
        data = self.cipher_aes.nonce + tag + ciphertext
        print('======== encrypt Client data ===============')
        ic(self.cipher_aes.nonce)
        ic(tag)
        ic(ciphertext)
        ic(data)
        return data

    @log_default(logger)
    @serializer
    def send_key(self):
        # ic(self.public_key)
        # a = pickle.dumps(SendKey(key=self.public_key))
        # ic(a)
        # res = pickle.loads(a)
        # ic(res)
        # ic(res.action)
        return SendKey(key=self.public_key)

    @log_default(logger)
    def authenticated(self, msg: Authenticate):
        if msg.result:
            self.auth = True
            print('online')
            self.status = 'online'
            self.feed_data(self.get_contacts())

    @log_default(logger)
    @serializer
    def authenticate(self):
        return Authenticate(username=self.username, password=self.password)

    @log_default(logger)
    @serializer
    def get_contacts(self):
        return GetContacts(login=self.username)

    @log_default(logger)
    @serializer
    def sender(self, msg):
        return msg

    @log_default(logger)
    @serializer
    def add_contact(self, name):
        return AddContact(username=name)

    @log_default(logger)
    @serializer
    def del_contact(self, name):
        return DelContact(username=name)

    @log_default(logger)
    @serializer
    def disconnect(self):
        return Quit()

    @log_default(logger)
    @serializer
    def presence(self):
        return Presence(username=self.username, status=self.status)

    @log_default(logger)
    @serializer
    def send_message(self, to, text):
        return Msg(to=to, from_=self.username, text=text)

    @log_default(logger)
    @serializer
    def get_messages(self, tm, contact=''):
        return GetMessages(time=tm, from_=contact)

    @log_default(logger)
    @serializer
    def join(self, room):
        return Join(room=room)

    @log_default(logger)
    @serializer
    def leave(self, room):
        return Leave(room=room)

    @log_default(logger)
    def on_msg(self, msg):
        print(time.ctime(time.time()) + f': {msg.from_}: {msg.text}')

    @log_default(logger)
    def close(self):
        self.auth = False
        self.feed_data('close')

    def _set_auth(self):
        self.auth = True

