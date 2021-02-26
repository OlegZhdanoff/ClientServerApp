import click
from socket import *
import time
import json


ENCODING = 'utf-8'
MAX_MSG_SIZE = 540


class Client:
    def __init__(self, account_name, password, status):
        self.account_name = account_name
        self.password = password
        self.status = status

    def authenticate(self):
        return {
            "action": "authenticate",
            "time": time.time(),
            "user": {
                    "account_name":  self.account_name,
                    "password":      self.password
            }
        }

    def disconnect(self):
        return {
            "action": "quit"
        }


@click.command()
@click.argument('address', default="localhost")
@click.argument('port', default=7777)
def start(address, port):
    user = Client('ivanov', '123', 'online')
    with socket(AF_INET, SOCK_STREAM) as s:  # Создает сокет TCP
        s.connect((address, port))  # Присваивает адрес и порт
        s.send(json.dumps(user.authenticate()).encode(ENCODING))
        tm = s.recv(MAX_MSG_SIZE)
        print(tm.decode(ENCODING))
        s.send(json.dumps(user.disconnect()).encode(ENCODING))
        tm = s.recv(MAX_MSG_SIZE)
        print(tm.decode(ENCODING))


if __name__ == '__main__':
    start()
