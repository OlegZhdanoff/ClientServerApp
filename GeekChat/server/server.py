import datetime
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP

from queue import Queue, Empty

from icecream import ic

from GeekChat.db.client import ClientStorage, Client
from GeekChat.db.client_history import ClientHistoryStorage
from GeekChat.db.contacts import ContactStorage
from GeekChat.db.messages import MessageStorage
from GeekChat.log.log_config import log_config, log_default
from GeekChat.messages import *
from GeekChat.services import serializer, LOCAL_ADMIN, MSG_LEN_NAME, MSG_END_LEN_NAME

logger = log_config('server', 'server.log')


class ClientInstance:

    def __init__(self, session, addr):
        """
        Client instance on server
        :param session: SQLAlchemy DB session
        :param addr: client IP-address
        """
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
        self.session_key = get_random_bytes(16)
        self.cipher_client_pk = None
        self.cipher_aes = AES.new(self.session_key, AES.MODE_EAX)

    def _find_client(self, msg):
        self.client = self.client_storage.auth_client(msg.username, msg.password)
        # ic(' ========== try to find client', msg.username, msg.password)

        if self.client == -1:
            try:
                if msg.username == LOCAL_ADMIN:
                    self.client_storage.add_client(msg.username, msg.password, is_admin=True)
                else:
                    self.client_storage.add_client(msg.username, msg.password)
                self.client = self.client_storage.auth_client(msg.username, msg.password)
            except ValueError:
                print(f"can't create new user, username {msg.username} already exists")
                self.client_logger.exception(f"can't create new user, username {msg.username} already exists")
        elif not self.client:
            print(f'username {msg.username} - wrong password')
            self.client_logger.exception(f'username {msg.username} - wrong password')
        # print(f'============= found_client -----> {self.client} <------')
        # ic(self.client)
        self.username = msg.username

    @log_default(logger)
    def feed_data(self, data):
        """
        send data to client
        Encrypt data if client exists in DB
        :param data: Any type of @dataclass from .messages or `close`
        """
        if isinstance(self.client, Client):
            data = self.encrypt_data(data)
        length = MSG_LEN_NAME + str(len(data)) + MSG_END_LEN_NAME
        data = length.encode() + data
        self.data_queue.put(data)

    def get_data(self):
        try:
            data = self.data_queue.get_nowait()
            self.data_queue.task_done()
            return data
        except Empty:
            pass

    @log_default(logger)
    def action_handler(self, msg, clients):
        """
        process messages from client
        :param msg: Any type of @dataclass from .messages
        """
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
        """
        encrypt session key with client public key and send to client
        :param msg: message with client public key
        :type msg: :class:`messages.SendKey`
        """
        client_public_key = RSA.import_key(msg.key)
        self.cipher_client_pk = PKCS1_OAEP.new(client_public_key)
        enc_session_key = self.cipher_client_pk.encrypt(self.session_key)
        self.feed_data(self.send_message(SendKey(key=enc_session_key)))
        return True

    @log_default(logger)
    def encrypt_data(self, data):
        """
        encrypt data with session key
        :param data: Any type of @dataclass from .messages
        :return: encrypted data
        """
        # Encrypt the data with the AES session key
        self.cipher_aes = AES.new(self.session_key, AES.MODE_EAX)
        ciphertext, tag = self.cipher_aes.encrypt_and_digest(data)
        data = self.cipher_aes.nonce + tag + ciphertext
        return data

    @log_default(logger)
    @serializer
    def authenticate(self, msg: Authenticate):
        """
        authenticating user on server, find user in DB, create user if not exists, check password
        :param msg: user credential
        :type msg: :class:`messages.Authenticate`
        :return: :class:`messages.Authenticate`
        """
        print(f'User {msg.username} is authenticating...')
        self.client_logger = logger.bind(username=msg.username, address=self.addr)
        self.client_logger.info('User is authenticating...')
        result_auth = self._check_pwd(msg)

        if result_auth == 200:
            print(f'User {msg.username} is authenticated')
            self.client_logger.info('User is authenticated')
            self.client_history_storage = ClientHistoryStorage(self.session, self.client)
            self.client_history_storage.add_record(self.addr, datetime.datetime.now())
            self.contacts = ContactStorage(self.session, self.client)
            self.messages = MessageStorage(self.session, self.client)

            return Authenticate(username=msg.username, result=True, alert='welcome to server')
        elif result_auth == 402:
            self.client_logger.info('User was entered wrong password')
            return Authenticate(username=msg.username,
                                result=False,
                                alert="This could be wrong password or no account with that name")
        elif result_auth == 409:
            self.client_logger.warning('Someone is already connected with the given user name')
            return Authenticate(username=msg.username,
                                result=False,
                                alert="Someone is already connected with the given user name")

    def _check_pwd(self, msg):
        self._find_client(msg)
        if self.client:
            if self.client == -1:
                return 409
            else:
                self.client.status = 'online'
                self.session.commit()
                return 200
        else:
            return 402

    @log_default(logger)
    def client_disconnect(self):
        """
        disconnect client from server, set client.status = 'disconnected'
        :return: False
        """
        if isinstance(self.client, Client):
            self.client.status = 'disconnected'
            self.session.commit()
        self.client_logger.info('User was disconnected')
        print(f'{self.username} was disconnected')
        return False

    def client_presence(self, msg: Presence):
        """
        process Presence message from client
        :param msg: client answer to Probe
        :type msg: :class:`messages.Presence`
        """
        if isinstance(self.client, Client):
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
        """
        send :class:`messages.Probe` request to client, if client doesn't authenticated just send
        informational :class:`messages.Response`
        :return: :class:`messages.Probe` or :class:`messages.Response`
        """
        if isinstance(self.client, Client):
            if self.pending_status:
                print("No presence() received from the user")
                self.client_logger.warning("No presence() received from the user")
                self.client.status = 'disconnected'
                self.session.commit()
                self.client_disconnect()
                self.pending_status = True
            return Probe()
        return Response(response=200, alert='server is waiting...')

    @log_default(logger)
    def on_msg(self, msg: Msg, clients):
        """
        process :class:`messages.Msg` from client, store message in DB, send to recipient, if his online
        :param msg: message from client
        :type msg: :class:`messages.Msg`
        :param clients: list of dict {conn: Client} with connected users
        """
        if msg.to[:1] == '#':
            for client in clients.values():
                if client.username != self.client.login:
                    client.feed_data(self.send_message(msg))
        else:
            for client in clients.values():
                if client.username == msg.to:
                    client.feed_data(self.send_message(msg))
                    break
        if isinstance(self.client, Client):
            client = self.client_storage.get_client(msg.to)
            if client:
                self.messages.add_message(client, msg.text)
            self.feed_data(self.send_response(200, 'message is received'))
        return True

    @log_default(logger)
    @serializer
    def send_message(self, msg):
        """
        send any type of messages to client
        :param msg: any type of messages to client
        :return: any type of messages to client
        """
        return msg

    @log_default(logger)
    @serializer
    def send_response(self, response, message):
        """
        send response to user
        :param response: response code
        :param message: response text
        :return: :class:`messages.Response`
        """
        return Response(response=response, alert=message)

    @log_default(logger)
    def join(self, msg: Join):
        """
        join client to channel
        :param msg: message from client
        :type msg: :class:`messages.Join`
        """
        self.client_logger(f'Client joined to <{msg.room}>')
        return True

    @log_default(logger)
    def leave(self, msg: Leave):
        """
        leave client from channel
        :param msg: message from client
        :type msg: :class:`messages.Leave`
        """
        self.client_logger(f'Client left <{msg.room}>')
        return True

    @log_default(logger)
    def get_contacts(self, msg: GetContacts):
        """
        get contact list for user
        :param msg: :class:`messages.GetContacts`
        """
        if self.contacts:
            self.feed_data(self.send_message(GetContacts(contacts=self.contacts.get_contacts())))
        return True

    @log_default(logger)
    def add_contact(self, msg: AddContact):
        """
        add specific user to contact list
        :param msg: message from user
        :type msg: :class:`messages.AddContact`
        """
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
    def del_contact(self, msg: DelContact):
        """
        add specific user to contact list
        :param msg: message from user
        :type msg: :class:`messages.DelContact`
        """
        try:
            self.contacts.del_contact(msg.username)
            self.feed_data(self.send_response(203, f'{msg.username} deleted from contacts'))
        except ValueError as e:
            self.client_logger.warning('Error')
            self.feed_data(self.send_response(405, e.__repr__()))
            return True
        return True

    @log_default(logger)
    def get_filtered_users(self, msg: FilterClients):
        """
        send filtered list of users from DB to client
        :param msg: message with mask
        """
        msg.users = self.client_storage.filter_clients(msg.pattern)
        self.feed_data(self.send_message(msg))
        return True

    @log_default(logger)
    def get_messages(self, msg: GetMessages):
        """
        find in DB and send chat messages between client and specific user
        :param msg: message from client
        """
        client = self.client_storage.get_client(msg.from_)
        ic('server get_messages', client)
        messages = self.messages.get_chat_msg(client)
        ic(messages)
        for item in messages:
            if item[2] == self.username:
                message = Msg(time=item[0].timestamp(), to=msg.from_, from_=item[2], text=item[1])
            else:
                message = Msg(time=item[0].timestamp(), to=self.username, from_=item[2], text=item[1])
            self.feed_data(self.send_message(message))
        return True
