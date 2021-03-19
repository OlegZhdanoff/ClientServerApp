import queue

import click
from socket import *
import time
# import json
# import structlog

from client.client import Client
from client.client_thread import ClientThread, SelectableQueue
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
        s.settimeout(0.1)
        s.connect((address, port))  # Присваивает адрес и порт
        # s.send(user.authenticate())

        gui_app_socket, client_app_socket = socketpair()
        sq_gui = SelectableQueue(gui_app_socket, client_app_socket)
        sq_client = SelectableQueue(client_app_socket, gui_app_socket)

        client_thread = ClientThread(s, user, sq_gui, sq_client)
        client_thread.start()

        while True:
            # tm = settings.recv_all(s)
            # tm = s.recv(settings.MAX_MSG_SIZE).decode(settings.ENCODING)
            # msg_list = settings.get_msg_list(tm)
            # for data in msg_list:
            #     msg = json.loads(data)
            #     if "action" in msg:
            #         user.action_handler(msg["action"], msg)
            #     elif "response" in msg:
            #         user.response_processor(msg["response"], msg)

            command = input('Command list:\t'
                            'q - exit\tm - message to all:\t')
            if command == 'q':
                # вызов функции disconnect from client_thread
                user.feed_data(None)
                break
            elif command == 'm':
                message = input('>> ')
                user.feed_data((user.send_message('#main', message)))

        client_thread.join()
        # s.send(user.disconnect())

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
