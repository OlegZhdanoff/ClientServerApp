import json

import click
from socket import *
import time
from contextlib import closing

ENCODING = 'utf-8'
MAX_MSG_SIZE = 640

def works_for_all(func):
    def inner(*args, **kwargs):
        print("Я могу декорировать любую функцию")
        return func(*args, **kwargs)
    return inner


class ClientInstance:
    def __init__(self):
        self.username = ''
        self.password = ''
        self.status = ''

    def authenticate(self, user):
        self.username = user["account_name"]
        self.password = user["password"]
        print(f'User {user["account_name"]} is authenticating...')
        result_auth = self.check_pwd(user)

        if result_auth == 200:
            return json.dumps({
                "response": 200,
                "time": time.time(),
                "alert": 'добро пожаловать в чат'
            }).encode(ENCODING)
        elif result_auth == 402:
            return json.dumps({
                "response": 402,
                "time": time.time(),
                "error": "This could be wrong password or no account with that name"
            }).encode(ENCODING)
        elif result_auth == 409:
            return json.dumps({
                "response": 409,
                "time": time.time(),
                "error": "Someone is already connected with the given user name"
            }).encode(ENCODING)

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

    def probe(self):
        return json.dumps({
            "action": "probe",
            "time": time.time(),
        }).encode(ENCODING)

    def msg(self, msg):
        pass

    def join(self, msg):
        pass

    def leave(self, chat_name):
        pass


@click.command()
@click.argument('address', default="localhost")
@click.argument('port', default=7777)
def start(address, port):
    print(address, port)
    with socket(AF_INET, SOCK_STREAM) as s:  # Создает сокет TCP
        s.bind((address, port))  # Присваивает адрес и порт
        s.listen(5)  # Переходит в режим ожидания запросов;
        # одновременно обслуживает не более 5 запросов.
        while True:
            client, addr = s.accept()  # Принять запрос на соединение
            with closing(client):
                print("Получен запрос на соединение от %s" % str(addr))
                # timestr = time.ctime(time.time()) + "\n"

                ci = ClientInstance()
                while True:
                    tm = client.recv(MAX_MSG_SIZE).decode(ENCODING)
                    msg = json.loads(tm)
                    if "action" in msg:
                        if not ci.action_handler(client, msg['action'], msg):
                            break


if __name__ == '__main__':

    start()
