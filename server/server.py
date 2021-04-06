import time
from queue import Queue, Empty

from client.client import Client
from db.client import ClientStorage
from db.client_history import ClientHistoryStorage
from log.log_config import log_config, log_default
from messages import *
from services import serializer

logger = log_config('server', 'server.log')


class ClientInstance:
    def __init__(self, Session, addr):
        # self.clients = {}
        # self.client_storage = ClientStorage(session)
        # self.client_history_storage = ClientHistoryStorage(session)
        self.Session = Session
        self.addr = addr
        self.client = None
        self.username = ''
        self.password = ''
        self.data_queue = Queue()
        self.pending_status = False
        self.client_logger = None

    def find_client(self, msg):  # как бы ищем клиента в БД
        with self.Session() as session:
            client_storage = ClientStorage(session)
            self.client = client_storage.auth_client(msg.username, msg.password)

            if not self.client:
                try:
                    client_storage.add_client(msg.username, msg.password)
                    self.client = client_storage.auth_client(msg.username, msg.password)
                except ValueError as e:
                    logger.exception(f'username {msg.username} already exists')

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
    @serializer
    def authenticate(self, msg):
        print(f'User {msg.username} is authenticating...')
        # logger.info(f'authenticate user {user["account_name"]}')
        self.client_logger = logger.bind(username=msg.username, address=self.addr)
        # user_on_server = self.clients.setdefault(addr, Client(*user.values()))
        result_auth = self.check_pwd(msg)

        if result_auth == 200:
            self.client_logger.info('User is authenticating')
            return Response(response=200, alert='добро пожаловать в чат')
        elif result_auth == 402:
            self.client_logger.info(f'User was entered wrong password')
            return Response(response=402, alert="This could be wrong password or no account with that name")
        elif result_auth == 409:
            self.client_logger.warning(f'User was entered wrong password')
            return Response(response=409, alert="Someone is already connected with the given user name")

    def check_pwd(self, msg):
        self.find_client(msg)
        if self.client:
            return 200 if self.client.status == 'disconnected' else 409
        else:
            return 402

    @log_default(logger)
    def client_disconnect(self):
        self.status = 'disconnected'
        self.client_logger.info('User was disconnected')
        print(f'{self.username} was disconnected')
        # client.close()
        return False

    def client_presence(self, msg):
        self.status = msg.status
        self.pending_status = False
        if self.status == 'disconnected':
            self.client_disconnect()

    @log_default(logger)
    def action_handler(self, msg, clients):
        if isinstance(msg, Authenticate):
            self.feed_data(self.authenticate(msg))
            return True
        elif isinstance(msg, Quit):
            return self.client_disconnect()
        elif isinstance(msg, Presence):
            self.client_presence(msg)
            return True
        elif isinstance(msg, Msg):
            self.on_msg(msg, clients)
            return True
        elif isinstance(msg, Join):
            return self.join(msg)
        elif isinstance(msg, Leave):
            return self.leave(msg)

    @log_default(logger)
    @serializer
    def probe(self):
        if self.pending_status:
            print("No presence() received from the user")
            self.client_logger.warning("No presence() received from the user")
            self.client_disconnect()
        self.pending_status = True
        return Probe()

    @log_default(logger)
    def on_msg(self, msg, clients):
        # for client in clients.values():
        #     print(client.username, self.username, msg['to'][:1])
        if msg.to[:1] == '#':
            for client in clients.values():
                if client.username != self.username:
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
        pass

    @log_default(logger)
    def leave(self, msg):
        pass
