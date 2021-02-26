import click
from socket import *
import time
from contextlib import closing

ADDRESS = 'localhost'
PORT = 7777

@click.command()
@click.argument('address', default="localhost")
@click.argument('port', default=7777)
def start(address, port):
    ADDRESS, PORT = address, port
    print(address, port)
    with socket(AF_INET, SOCK_STREAM) as s:  # Создает сокет TCP
        s.bind((ADDRESS, PORT))  # Присваивает адрес и порт
        s.listen(5)  # Переходит в режим ожидания запросов;
        # одновременно обслуживает не более
        # 5 запросов.
        while True:
            client, addr = s.accept()  # Принять запрос на соединение
            with closing(client) as cl:
                print("Получен запрос на соединение от %s" % str(addr))
                timestr = time.ctime(time.time()) + "\n"

                # Обратите внимание, дальнейшая работа ведётся с сокетом клиента
                client.send(timestr.encode('ascii'))  # <- По сети должны передаваться байты,
                # поэтому выполняется кодирование строки

# print(ADDRESS, PORT)
if __name__ == '__main__':

    start()
    # print(ADDRESS, PORT)
