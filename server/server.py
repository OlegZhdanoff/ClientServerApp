import time
from queue import Queue, Empty

from client.client import Client
from log.log_config import log_config, log_default
from messages import *
from services import serializer

logger = log_config('server', 'server.log')


class Server:
    def __init__(self, conn, addr):
        # self.clients = {}
        self.conn = conn
        self.addr = addr
        self.status = ''
        self.username = ''
        self.password = ''
        self.data_queue = Queue()

    def find_client(self, username):  # как бы ищем клиента в БД
        self.username = username
        self.password = '123'
        self.status = 'disconnected'
        # try:
        #     idx = self.clients.index(cl)
        #     return self.clients[idx]
        # except ValueError:
        #     print(f'{cl} is not found')
        #     return False

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
        logger_with_name = logger.bind(username=msg.username, address=self.addr)
        # user_on_server = self.clients.setdefault(addr, Client(*user.values()))
        result_auth = self.check_pwd(msg)

        if result_auth == 200:
            logger_with_name.info('User is authenticating')
            return Response(response=200, alert='добро пожаловать в чат')
        elif result_auth == 402:
            logger_with_name.info(f'User was entered wrong password')
            return Response(response=402, alert="This could be wrong password or no account with that name")
        elif result_auth == 409:
            logger_with_name.warning(f'User was entered wrong password')
            return Response(response=409, alert="Someone is already connected with the given user name")

    def check_pwd(self, msg):
        self.find_client(msg.username)
        if self.username == msg.username and self.password == msg.password:
            return 200 if self.status == 'disconnected' else 409
        else:
            return 402

    @log_default(logger)
    def client_disconnect(self):
        self.status = 'disconnected'
        logger_with_name = logger.bind(username=self.username, address=self.addr)
        logger_with_name.info('User was disconnected')
        print(f'{self.username} was disconnected')
        # client.close()
        return False

    def client_presence(self, msg):
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

    @log_default(logger)
    @serializer
    def probe(self):
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
