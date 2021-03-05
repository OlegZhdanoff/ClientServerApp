import click
from socket import *
import time
import json
import structlog

from client.client import Client
from log.log_config import log_config

ENCODING = 'utf-8'
MAX_MSG_SIZE = 640

logger = log_config('chat_client', 'client.log')


@click.command()
@click.argument('address', default="www.ya.ru")
@click.argument('port', default=7777)
def start(address, port):
    user = Client('ivanov', '123', 'online')
    try:
        s = socket(AF_INET, SOCK_STREAM)  # Создает сокет TCP
        s.connect((address, port))  # Присваивает адрес и порт
        s.send(user.authenticate())
        tm = s.recv(MAX_MSG_SIZE)
        print(json.loads(tm.decode(ENCODING)))
        # time.sleep(60)
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
