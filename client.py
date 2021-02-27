import click
from socket import *
import time
import json


ENCODING = 'utf-8'
MAX_MSG_SIZE = 640


class Client:
    def __init__(self, account_name, password, status):
        self.account_name = account_name
        self.password = password
        self.status = status

    def authenticate(self):
        return json.dumps({
            "action": "authenticate",
            "time": time.time(),
            "user": {
                    "account_name":  self.account_name,
                    "password":      self.password
            }
        }).encode(ENCODING)

    def disconnect(self):
        return json.dumps({
            "action": "quit"
        }).encode(ENCODING)

    def presence(self):
        return json.dumps({
            "action": "presence",
            "time": time.time(),
            "type": self.status,
            "user": {
                    "account_name":  self.account_name,
                    "password":      self.password
            }
        }).encode(ENCODING)

    def action_handler(self, action, **kwargs):
        if action == 'probe':
            return self.presence()



@click.command()
@click.argument('address', default="localhost")
@click.argument('port', default=7777)
def start(address, port):
    user = Client('ivanov', '123', 'online')
    with socket(AF_INET, SOCK_STREAM) as s:  # Создает сокет TCP
        s.connect((address, port))  # Присваивает адрес и порт
        s.send(user.authenticate())
        tm = s.recv(MAX_MSG_SIZE)
        print(json.loads(tm.decode(ENCODING)))
        s.send(user.disconnect())
        # tm = s.recv(MAX_MSG_SIZE)
        # print(tm.decode(ENCODING))


if __name__ == '__main__':
    start()
