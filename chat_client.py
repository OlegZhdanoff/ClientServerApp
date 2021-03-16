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
        tm = s.recv(settings.MAX_MSG_SIZE).decode(settings.ENCODING)
        # msg = json.loads(tm)
        # if "response" in msg:
        #     user.response_processor(msg["response"], msg)
        while True:
            command = input('Command list:\t'
                            'q - exit\tm - message to all\t')
            if command == 'q':
                break
            elif command == 'm':
                message = input('Your message: ')
                s.send(user.send_message('#main', message))

            tm = s.recv(settings.MAX_MSG_SIZE).decode(settings.ENCODING)
            print("tm: ", tm)
            for line in tm:
                print(line)
            msg = json.loads(line)
            print(msg)
            if "action" in msg:
                user.action_handler(msg["action"], msg)
            elif "response" in msg:
                user.response_processor(msg["response"], msg)
        s.send(user.disconnect())
    except gaierror as e:
        logger.exception(f'Incorrect server IP-address {address}:{port}')
    except TimeoutError as e:
        logger.exception(f'Wrong answer from server {address}:{port}')
    except ConnectionRefusedError as e:
        logger.exception(f'Server {address}:{port} is offline')
    except Exception as e:
        logger.exception(f'Error connection with server {address}:{port} - {e.args}')
    finally:
        s.close()


if __name__ == '__main__':
    start()
