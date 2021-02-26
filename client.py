import click
from socket import *
import time


@click.command()
@click.argument('address', default="localhost")
@click.argument('port', default=7777)
def start(address, port):
    with socket(AF_INET, SOCK_STREAM) as s:  # Создает сокет TCP
        s.connect((address, port))  # Присваивает адрес и порт
        tm = s.recv(640)
        print("Текущее время: %s" % tm.decode('utf-8'))


if __name__ == '__main__':
    start()
