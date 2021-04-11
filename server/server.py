import datetime
from queue import Queue, Empty

from db.client import ClientStorage
from db.client_history import ClientHistoryStorage
from db.contacts import ContactStorage
from log.log_config import log_config, log_default
from messages import *
from services import serializer, LOCAL_ADMIN

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
        # self.password = ''
        self.data_queue = Queue()
        self.pending_status = False
        self.client_logger = None

    def find_client(self, msg):
        self.client = self.client_storage.get_client(msg.username, msg.password)

        if not self.client:
            try:
                self.client_storage.add_client(msg.username, msg.password)
                self.client = self.client_storage.get_client(msg.username, msg.password)
            except ValueError as e:
                print(f'username {msg.username} already exists')
                self.client_logger.exception(f'username {msg.username} already exists')
        # print(f'============= find_client -----> {self.client} <------')
        self.username = msg.username

    @log_default(logger)
    def feed_data(self, data):
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

    @log_default(logger)
    @serializer
    def authenticate(self, msg):
        print(f'User {msg.username} is authenticating...')
        self.client_logger = logger.bind(username=msg.username, address=self.addr)
        result_auth = self.check_pwd(msg)

        if result_auth == 200:
            self.client_logger.info('User is authenticating')
            self.client_history_storage = ClientHistoryStorage(self.session, self.client)
            self.client_history_storage.add_record(self.addr, datetime.datetime.now())
            # self.client_history_storage.get_history()
            # print(type(self.client_storage.get_all()))
            # print(self.client_storage.get_all())
            self.contacts = ContactStorage(self.session, self.client)
            return Response(response=200, alert='добро пожаловать в чат')
        elif result_auth == 402:
            self.client_logger.info(f'User was entered wrong password')
            return Response(response=402, alert="This could be wrong password or no account with that name")
        elif result_auth == 409:
            self.client_logger.warning(f'Someone is already connected with the given user name')
            return Response(response=409, alert="Someone is already connected with the given user name")

    def check_pwd(self, msg):
        self.find_client(msg)
        if self.client:
            if self.client.status == 'disconnected' or self.client.login == LOCAL_ADMIN:
                self.client.status = 'online'
                self.session.commit()
                return 200
            else:
                return 409
        else:
            return 402

    @log_default(logger)
    def client_disconnect(self):
        self.client.status = 'disconnected'
        self.session.commit()
        self.client_logger.info('User was disconnected')
        print(f'{self.client.login} was disconnected')
        return False

    def client_presence(self, msg):
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
                if client.username == msg['to']:
                    client.feed_data(self.send_message(msg))
                    break
        self.feed_data(self.send_response(200, 'message is received'))

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
        self.feed_data(self.send_response(200, self.contacts.get_contacts()))
        return True

    @log_default(logger)
    def add_contact(self, msg):
        try:
            print('===call to add contact === ')
            self.contacts.add_contact(msg.username)
            self.feed_data(self.send_response(201, f'{msg.username} added to contacts'))
        except ValueError as e:
            self.client_logger.warning('Error')
            self.feed_data(self.send_response(405, e.__repr__()))
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
