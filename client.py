import click
from socket import *
import time


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
        tm = s.recv(640)
        print("Текущее время: %s" % tm.decode('utf-8'))


if __name__ == '__main__':
    start()
