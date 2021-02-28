import click
from socket import *
import time
import json
from client.client import Client

ENCODING = 'utf-8'
MAX_MSG_SIZE = 640


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
