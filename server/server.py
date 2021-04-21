import datetime
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP

from queue import Queue, Empty

from icecream import ic

from db.client import ClientStorage, Client
from db.client_history import ClientHistoryStorage
from db.contacts import ContactStorage
from db.messages import MessageStorage
from log.log_config import log_config, log_default
from messages import *
from services import serializer, LOCAL_ADMIN, MSG_LEN_NAME, MSG_END_LEN_NAME

logger = log_config('server', 'server.log')


class ClientInstance:

    def __init__(self, session, addr):

        self.session = session
        self.client_history_storage = None
        self.client_storage = ClientStorage(self.session)
        self.contacts = None
        self.addr = addr
        self.client = None
        self.username = ''
        self.data_queue = Queue()
        self.pending_status = False
        self.client_logger = None
        self.messages = None

        key = RSA.generate(2048)
        self.public_key = key.publickey().export_key()
        self.private_key = key.export_key()
        # self.client_public_key = None
        self.session_key = get_random_bytes(16)
        self.cipher_client_pk = None
        self.cipher_aes = AES.new(self.session_key, AES.MODE_EAX)

    def find_client(self, msg):
        self.client = self.client_storage.auth_client(msg.username, msg.password)
        ic(' ========== find client', msg.username, msg.password)

        if self.client == -1:
            try:
                if msg.username == LOCAL_ADMIN:
                    self.client_storage.add_client(msg.username, msg.password, is_admin=True)
                else:
                    self.client_storage.add_client(msg.username, msg.password)
                self.client = self.client_storage.auth_client(msg.username, msg.password)
            except ValueError as e:
                print(f"can't create new user, username {msg.username} already exists")
                self.client_logger.exception(f"can't create new user, username {msg.username} already exists")
        elif not self.client:
            print(f'username {msg.username} - wrong password')
            self.client_logger.exception(f'username {msg.username} - wrong password')
        print(f'============= find_client -----> {self.client} <------')
        ic(self.client.login)
        self.username = msg.username

    @log_default(logger)
    def feed_data(self, data):
        if isinstance(self.client, Client):
            # print('========== server feed encrypted data ===========')
            # ic(data)
            data = self.encrypt_data(data)
        # else:
            # print('========== server feed plain data ===========')
            # ic(data)
        length = MSG_LEN_NAME + str(len(data)) + MSG_END_LEN_NAME
        data = length.encode() + data
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
    def action_handler(self, msg, clients):
        if isinstance(msg, Authenticate):
            self.feed_data(self.authenticate(msg))
            return True
        elif isinstance(msg, Quit):
            return self.client_disconnect()
        elif isinstance(msg, Presence):
            return self.client_presence(msg)
        elif isinstance(msg, Msg):
            self.on_msg(msg, clients)
            return True
        elif isinstance(msg, GetMessages):
            return self.get_messages(msg)
        elif isinstance(msg, Join):
            return self.join(msg)
        elif isinstance(msg, Leave):
            return self.leave(msg)
        elif isinstance(msg, GetContacts):
            return self.get_contacts(msg)
        elif isinstance(msg, AddContact):
            return self.add_contact(msg)
        elif isinstance(msg, DelContact):
            return self.del_contact(msg)
        elif isinstance(msg, FilterClients):
            return self.get_filtered_users(msg)
        elif isinstance(msg, SendKey):
            return self.send_secret_key(msg)

    @log_default(logger)
    def send_secret_key(self, msg: SendKey):
        client_public_key = RSA.import_key(msg.key)
        self.cipher_client_pk = PKCS1_OAEP.new(client_public_key)
        enc_session_key = self.cipher_client_pk.encrypt(self.session_key)
        # print('======= server send_secret_key ==========')
        # ic(msg.key)
        # ic(client_public_key)
        # ic(self.cipher_client_pk)
        # ic(enc_session_key)
        self.feed_data(self.send_message(SendKey(key=enc_session_key)))
        return True

    @log_default(logger)
    def encrypt_data(self, data):
        print('======== encrypt Server data ===============')
        ic(data)
        ic(self.session_key)
        # Encrypt the data with the AES session key
        self.cipher_aes = AES.new(self.session_key, AES.MODE_EAX)
        ciphertext, tag = self.cipher_aes.encrypt_and_digest(data)
        data = self.cipher_aes.nonce + tag + ciphertext
        ic(self.cipher_aes.nonce)
        ic(tag)
        ic(ciphertext)
        return data

    @log_default(logger)
    @serializer
    def authenticate(self, msg):
        print(f'User {msg.username} is authenticating...')
        self.client_logger = logger.bind(username=msg.username, address=self.addr)
        self.client_logger.info('User is authenticating...')
        result_auth = self.check_pwd(msg)

        if result_auth == 200:
            print(f'User {msg.username} is authenticated')
            self.client_logger.info('User is authenticated')
            self.client_history_storage = ClientHistoryStorage(self.session, self.client)
            self.client_history_storage.add_record(self.addr, datetime.datetime.now())
            self.contacts = ContactStorage(self.session, self.client)
            self.messages = MessageStorage(self.session, self.client)
            # if self.messages.get_from_owner_messages():
            #     print(type(self.messages.get_from_owner_messages()[0]))
            #     print(self.messages.get_from_owner_messages()[0].message)

            return Authenticate(username=msg.username, result=True)
        elif result_auth == 402:
            self.client_logger.info(f'User was entered wrong password')
            return Response(response=402, alert="This could be wrong password or no account with that name")
        elif result_auth == 409:
            self.client_logger.warning(f'Someone is already connected with the given user name')
            return Response(response=409, alert="Someone is already connected with the given user name")

    def check_pwd(self, msg):
        self.find_client(msg)
        if self.client:
            # if self.client.status == 'disconnected' or self.client.login == LOCAL_ADMIN:
            if self.client == -1:
                return 409
            else:
                self.client.status = 'online'
                self.session.commit()
                return 200
            # elif self.client == -1:
            #     return 409
        else:
            return 402

    @log_default(logger)
    def client_disconnect(self):
        if self.client:
            self.client.status = 'disconnected'
            self.session.commit()
        self.client_logger.info('User was disconnected')
        print(f'{self.username} was disconnected')
        return False

    def client_presence(self, msg):
        if not self.client:
            return self.client_disconnect()
        else:
            print(self.client)
            if not self.client.status == msg.status:
                self.client.status = msg.status
                self.session.commit()
            self.pending_status = False
            if self.client.status == 'disconnected':
                return self.client_disconnect()
            return True

    @log_default(logger)
    @serializer
    def probe(self):
        if self.pending_status:
            print("No presence() received from the user")
            self.client_logger.warning("No presence() received from the user")
            self.client.status = 'disconnected'
            self.session.commit()
            self.client_disconnect()
        self.pending_status = True
        return Probe()

    @log_default(logger)
    def on_msg(self, msg, clients):
        if msg.to[:1] == '#':
            for client in clients.values():
                if client.username != self.client.login:
                    client.feed_data(self.send_message(msg))
        else:
            for client in clients.values():
                if client.username == msg.to:
                    client.feed_data(self.send_message(msg))
                    break
        client = self.client_storage.get_client(msg.to)
        # ic(client)
        if client:
            self.messages.add_message(client, msg.text)
        self.feed_data(self.send_response(200, 'message is received'))
        return True

    @log_default(logger)
    @serializer
    def send_message(self, msg):
        return msg

    @log_default(logger)
    @serializer
    def send_response(self, response, message):
        return Response(response=response, alert=message)

    @log_default(logger)
    def join(self, msg):
        self.client_logger(f'Client joined to <{msg.room}>')

    @log_default(logger)
    def leave(self, msg):
        self.client_logger(f'Client left <{msg.room}>')

    @log_default(logger)
    def get_contacts(self, msg):
        self.feed_data(self.send_message(GetContacts(contacts=self.contacts.get_contacts())))
        return True

    @log_default(logger)
    def add_contact(self, msg):
        try:
            print(f'===call to add contact {msg.username} === ')
            self.contacts.add_contact(msg.username)
            self.feed_data(self.send_response(201, f'{msg.username} added to contacts'))
            print(f'{msg.username} added to contacts')
        except ValueError as e:
            self.client_logger.warning('Error')
            self.feed_data(self.send_response(405, e.__repr__()))
            return True
        return True

    @log_default(logger)
    def del_contact(self, msg):
        try:
            self.contacts.del_contact(msg.username)
            self.feed_data(self.send_response(203, f'{msg.username} deleted from contacts'))
        except ValueError as e:
            self.client_logger.warning('Error')
            self.feed_data(self.send_response(405, e.__repr__()))
            return True
        return True

    @log_default(logger)
    def get_filtered_users(self, msg):
        msg.users = self.client_storage.filter_clients(msg.pattern)
        self.feed_data(self.send_message(msg))
        return True

    @log_default(logger)
    def get_messages(self, msg):
        client = self.client_storage.get_client(msg.from_)
        ic('server get_messages', client)
        # messages = self.messages.get_to_owner_msg_from_time(msg.from_, datetime.datetime.fromtimestamp(msg.time))
        messages = self.messages.get_chat_msg(client)
        ic(messages)
        for item in messages:
            if item[2] == self.username:
                message = Msg(time=item[0].timestamp(), to=msg.from_, from_=item[2], text=item[1])
            else:
                message = Msg(time=item[0].timestamp(), to=self.username, from_=item[2], text=item[1])
            self.feed_data(self.send_message(message))
        return True
        # for message in messages:
        #     # print(type(self.messages.get_from_owner_messages()[0]))
        #     # print(self.messages.get_from_owner_messages()[0].message)
        #     self.feed_data(self.send_message(Msg(
        #         time=message.when,
        #         to=self.username,
        #         from_=message.from_id,
        #         text=message.message
        #     )))