import time
import structlog

from client.client import Client
from log.log_config import log_config, log_default
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
        self.data = b''

    def find_client(self, user):  # как бы ищем клиента в БД
        self.username = user["account_name"]
        self.password = user["password"]
        self.status = 'disconnected'
        # try:
        #     idx = self.clients.index(cl)
        #     return self.clients[idx]
        # except ValueError:
        #     print(f'{cl} is not found')
        #     return False

    @log_default(logger)
    @serializer
    def authenticate(self, user):
        print(f'User {user["account_name"]} is authenticating...')
        # logger.info(f'authenticate user {user["account_name"]}')
        logger_with_name = logger.bind(account_name=user["account_name"], address=self.addr)
        # user_on_server = self.clients.setdefault(addr, Client(*user.values()))
        result_auth = self.check_pwd(user)

        if result_auth == 200:
            logger_with_name.info('User is authenticating')
            return {
                "response": 200,
                "time": time.time(),
                "alert": 'добро пожаловать в чат'
            }
        elif result_auth == 402:
            logger_with_name.info(f'User was entered wrong password')
            return {
                "response": 402,
                "time": time.time(),
                "error": "This could be wrong password or no account with that name"
            }
        elif result_auth == 409:
            logger_with_name.warning(f'User was entered wrong password')
            return {
                "response": 409,
                "time": time.time(),
                "error": "Someone is already connected with the given user name"
            }

    def check_pwd(self, user):
        self.find_client(user)
        if self.username == user["account_name"] and self.password == user["password"]:
            return 200 if self.status == 'disconnected' else 409
        else:
            return 402

    @log_default(logger)
    def client_disconnect(self):
        self.status = 'disconnected'
        logger_with_name = logger.bind(account_name=self.username, address=self.addr)
        logger_with_name.info('User was disconnected')
        print(f'{self.username} was disconnected')
        # client.close()
        return False

    def client_presence(self, msg):
        pass

    @log_default(logger)
    def action_handler(self, action, msg, clients):
        if action == 'authenticate':
            print(msg)
            self.data += self.authenticate(msg['user'])
            return self.data
        elif action == 'quit':
            return self.client_disconnect()
        elif action == 'presence':
            return self.client_presence(msg)
        elif action == 'msg':
            self.msg(msg, clients)
            return True
        elif action == 'join':
            return self.join(msg)
        elif action == 'leave':
            return self.leave(msg)

    @log_default(logger)
    @serializer
    def probe(self):
        return {
            "action": "probe",
            "time": time.time(),
        }

    @log_default(logger)
    def msg(self, msg, clients):
        # for client in clients.values():
        #     print(client.username, self.username, msg['to'][:1])
        if msg['to'][:1] == '#':
            for client in clients.values():
                if client.username != self.username:
                    client.data += self.send_message(msg)
        else:
            for client in clients.values():
                if client.username == msg['to']:
                    client.data += self.send_message(msg)
                    break
        self.data += self.send_response(200, 'message is received')

    @log_default(logger)
    @serializer
    def send_message(self, msg):
        return {
            "action": "msg",
            "time": time.time(),
            "to": msg['to'],
            "from": self.username,
            "message": msg['message']
        }

    @log_default(logger)
    @serializer
    def send_response(self, response, message):
        if response == 200:
            return {
                    "response": 200,
                    "time": time.time(),
                    "alert": message
                }

    @log_default(logger)
    def join(self, msg):
        pass

    @log_default(logger)
    def leave(self, msg):
        pass
