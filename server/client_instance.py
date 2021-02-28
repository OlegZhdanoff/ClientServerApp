import json
import time

ENCODING = 'utf-8'
MAX_MSG_SIZE = 640


def send_json(func):
    def inner(*args, **kwargs):
        return json.dumps(func(*args, **kwargs)).encode(ENCODING)
    return inner


class ClientInstance:
    def __init__(self):
        self.username = ''
        self.password = ''
        self.status = ''

    @send_json
    def authenticate(self, user):
        self.username = user["account_name"]
        self.password = user["password"]
        print(f'User {user["account_name"]} is authenticating...')
        result_auth = self.check_pwd(user)

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

    def check_pwd(self, user):
        return 200

    def client_disconnect(self, client):
        print(f'User {self.username} is disconnected')
        client.close()
        return False

    def client_presence(self, msg):
        pass

    def action_handler(self, client, action, msg):
        if action == 'authenticate':
            print(msg)
            return client.send(self.authenticate(msg['user']))
        elif action == 'quit':
            return self.client_disconnect(client)
        elif action == 'presence':
            return self.client_presence(msg)
        elif action == 'msg':
            return self.msg(msg)
        elif action == 'join':
            return self.join(msg)
        elif action == 'leave':
            return self.leave(msg['user'])

    @send_json
    def probe(self):
        return {
            "action": "probe",
            "time": time.time(),
        }

    def msg(self, msg):
        pass

    def join(self, msg):
        pass

    def leave(self, chat_name):
        pass