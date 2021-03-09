import json
import structlog
import click
from socket import *
import time
from contextlib import closing

from server.server import Server
from log.log_config import log_config
import settings

logger = log_config('server', 'server.log')


@click.command()
@click.argument('address', default=settings.DEFAULT_SERVER_IP)
@click.argument('port', default=settings.DEFAULT_SERVER_PORT)
def start(address, port):
    print(address, port)
    try:
        s = socket(AF_INET, SOCK_STREAM)
        # with socket(AF_INET, SOCK_STREAM) as s:  # Создает сокет TCP
        s.bind((address, port))  # Присваивает адрес и порт
        s.listen(5)  # Переходит в режим ожидания запросов;
        # одновременно обслуживает не более 5 запросов.
        ci = Server()
        logger.info(f'Server is started on {address}:{port}')
        while True:
            client, addr = s.accept()  # Принять запрос на соединение
            with closing(client):
                print("Получен запрос на соединение от %s" % str(addr))
                # timestr = time.ctime(time.time()) + "\n"

                # ci = Server()
                while True:
                    tm = client.recv(settings.MAX_MSG_SIZE).decode(settings.ENCODING)
                    msg = json.loads(tm)
                    if "action" in msg:
                        if not ci.action_handler(client, msg['action'], msg, addr[0]):
                            break
    except OSError:
        logger.exception('Server cannot create socket')
    finally:
        s.close()
        logger.info(f'Server {address}:{port} was closed ')


if __name__ == '__main__':

    start()
