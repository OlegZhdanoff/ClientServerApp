import json
import time
from client.client import Client

ENCODING = 'utf-8'
MAX_MSG_SIZE = 640


def send_json(func):
    def inner(*args, **kwargs):
        return json.dumps(func(*args, **kwargs)).encode(ENCODING)
    return inner


class Server:
    def __init__(self):
        self.clients = {}

    # def find_client(self, cl: Client):
    #     try:
    #         idx = self.clients.index(cl)
    #         return self.clients[idx]
    #     except ValueError:
    #         print(f'{cl} is not found')
    #         return False

    @send_json
    def authenticate(self, user, addr):
        print(f'User {user["account_name"]} is authenticating...')
        user_on_server = self.clients.setdefault(addr, Client(*user.values()))
        result_auth = self.check_pwd(user_on_server, user)

        if result_auth == 200:
            return {
                "response": 200,
                "time": time.time(),
                "alert": 'добро пожаловать в чат'
            }
        elif result_auth == 402:
            return {
                "response": 402,
                "time": time.time(),
                "error": "This could be wrong password or no account with that name"
            }
        elif result_auth == 409:
            return {
                "response": 409,
                "time": time.time(),
                "error": "Someone is already connected with the given user name"
            }

    def check_pwd(self, user_on_server, user):
        if user_on_server.account_name == user["account_name"] and user_on_server.password == user["password"]:
            return 200 if user_on_server.status == 'disconnected' else 409
        else:
            return 402

    def client_disconnect(self, client, addr):
        print(f'User {self.clients[addr]} is disconnected')
        self.clients[addr].status = 'disconnected'
        client.close()
        return False

    def client_presence(self, msg, addr):
        pass

    def action_handler(self, client, action, msg, addr):
        if action == 'authenticate':
            print(msg)
            return client.send(self.authenticate(msg['user'], addr))
        elif action == 'quit':
            return self.client_disconnect(client, addr)
        elif action == 'presence':
            return self.client_presence(msg, addr)
        elif action == 'msg':
            return self.msg(msg, addr)
        elif action == 'join':
            return self.join(msg, addr)
        elif action == 'leave':
            return self.leave(msg, addr)

    @send_json
    def probe(self):
        return {
            "action": "probe",
            "time": time.time(),
        }

    def msg(self, msg, addr):
        pass

    def join(self, msg, addr):
        pass

    def leave(self, msg, addr):
        pass