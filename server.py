import click
from socket import *
import time
from contextlib import closing

ENCODING = 'utf-8'


class Server:
    def __init__(self, address, port):
        self.address = address
        self.port = port

    def authenticate(self, username, password):
        result_auth = self.check_pwd(username, password)
        if result_auth == 200:
            return {
                "response": 200,
                "alert": "добро пожаловать в чат"
            }
        elif result_auth == 402:
            return {
                "response": 402,
                "error": "This could be wrong password or no account with that name"
            }
        elif result_auth == 409:
            return {
                "response": 409,
                "error": "Someone is already connected with the given user name"
            }

    def check_pwd(self, username, password):
        return 200

    def client_disconnect(self, username):
        pass

    def event_handler(self, action):
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
            with closing(client) as cl:
                print("Получен запрос на соединение от %s" % str(addr))
                timestr = time.ctime(time.time()) + "\n"
                client.send(timestr.encode(ENCODING))


if __name__ == '__main__':

    start()
