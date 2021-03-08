import json

import click
from socket import *
import time
from contextlib import closing
from server.server import Server

ENCODING = 'utf-8'
MAX_MSG_SIZE = 640


@click.command()
@click.argument('address', default="localhost")
@click.argument('port', default=7777)
def start(address, port):
    print(address, port)
    with socket(AF_INET, SOCK_STREAM) as s:  # Создает сокет TCP
        s.bind((address, port))  # Присваивает адрес и порт
        s.listen(5)  # Переходит в режим ожидания запросов;
        # одновременно обслуживает не более 5 запросов.
        ci = Server()
        while True:
            client, addr = s.accept()  # Принять запрос на соединение
            with closing(client):
                print("Получен запрос на соединение от %s" % str(addr))
                # timestr = time.ctime(time.time()) + "\n"

                # ci = Server()
                while True:
                    tm = client.recv(MAX_MSG_SIZE).decode(ENCODING)
                    msg = json.loads(tm)
                    if "action" in msg:
                        if not ci.action_handler(client, msg['action'], msg, addr[0]):
                            break


if __name__ == '__main__':

    start()
