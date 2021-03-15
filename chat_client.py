import click
from socket import *
import time
import json
import structlog

from client.client import Client
from log.log_config import log_config
import settings

logger = log_config('chat_client', 'client.log')


@click.command()
@click.argument('address', default=settings.DEFAULT_SERVER_IP)
@click.argument('port', default=settings.DEFAULT_SERVER_PORT)
@click.option('--username', default='ivanov', help='username')
def start(address, port, username):
    user = Client(username, '123', 'online')
    try:
        s = socket(AF_INET, SOCK_STREAM)  # Создает сокет TCP
        s.connect((address, port))  # Присваивает адрес и порт
        s.send(user.authenticate())
        tm = s.recv(settings.MAX_MSG_SIZE)
        print(json.loads(tm.decode(settings.ENCODING)))
        # time.sleep(60)
        s.send(user.send_message('#main', 'hello'))
        tm = s.recv(settings.MAX_MSG_SIZE)
        print(json.loads(tm.decode(settings.ENCODING)))
        time.sleep(5)
        s.send(user.disconnect())
        # tm = s.recv(MAX_MSG_SIZE)
        # print(tm.decode(ENCODING))
    except gaierror as e:
        logger.exception(f'Incorrect server IP-address {address}:{port}')
    except TimeoutError as e:
        logger.exception(f'Wrong answer from server {address}:{port}')
    except ConnectionRefusedError as e:
        logger.exception(f'Server {address}:{port} is offline')
    except Exception as e:
        logger.exception(f'Error connection with server {address}:{port}')
    finally:
        s.close()


if __name__ == '__main__':
    start()
