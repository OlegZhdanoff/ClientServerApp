import time
from queue import Queue, Empty

from sqlalchemy.orm import sessionmaker

from client.client import Client
from db.client import ClientStorage
from db.client_history import ClientHistoryStorage
from log.log_config import log_config, log_default
from messages import *
from services import serializer, LOCAL_ADMIN

logger = log_config('server', 'server.log')


class ClientInstance:
    def __init__(self, engine, addr):
        # self.clients = {}

        # self.client_storage = ClientStorage(session)
        # self.client_storage = client_storage
        # self.client_history_storage = ClientHistoryStorage(session)
        # self.client_history_storage = client_history_storage
        self.Session = sessionmaker(bind=engine)
        self.session = self.Session()
        self.client_history_storage = ClientHistoryStorage(self.session)
        self.client_storage = ClientStorage(self.session)
        self.addr = addr
        self.client = None
        self.username = ''
        # self.password = ''
        self.data_queue = Queue()
        self.pending_status = False
        self.client_logger = None

    def find_client(self, msg):  # как бы ищем клиента в БД
        # with self.session.begin():
        # client_storage = ClientStorage(session)
        self.client = self.client_storage.get_client(msg.username, msg.password)

        if not self.client:
            try:
                self.client_storage.add_client(msg.username, msg.password)
                self.client = self.client_storage.get_client(msg.username, msg.password)
            except ValueError as e:
                print(f'username {msg.username} already exists')
                logger.exception(f'username {msg.username} already exists')
        print(f'============= find_client -----> {self.client} <------')
        # print(msg.username)

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
        self.client_logger = logger.bind(username=msg.username, address=self.addr)
        result_auth = self.check_pwd(msg)

        if result_auth == 200:
            self.client_logger.info('User is authenticating')
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
                # with self.Session() as session:
                #     client_storage = ClientStorage(session)
                self.client.status = 'online'
                self.session.commit()
                # self.client_storage.set_status(self.client)
                return 200
            else:
                return 409
        else:
            return 402

    @log_default(logger)
    def client_disconnect(self):
        self.client.status = 'disconnected'
        self.session.commit()
        # with self.Session() as session:
        #     client_storage = ClientStorage(session)
        # self.client_storage.set_status(self.client)
        self.client_logger.info('User was disconnected')
        print(f'{self.client.login} was disconnected')
        # client.close()
        return False

    def client_presence(self, msg):
        if not self.client.status == msg.status:
            self.client.status = msg.status
            self.session.commit()
        # with self.Session() as session:
        #     client_storage = ClientStorage(session)
        #     self.client_storage.set_status(self.client)
        self.pending_status = False
        if self.client.status == 'disconnected':
            return self.client_disconnect()
        return True

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
        # print('client', self.client)
        return msg

    @log_default(logger)
    @serializer
    def send_response(self, response, message):
        # print('client', self.client)
        return Response(response=response, alert=message)

    @log_default(logger)
    def join(self, msg):
        pass

    @log_default(logger)
    def leave(self, msg):
        pass
