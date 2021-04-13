import selectors
import sys

import click
from socket import *

from PyQt5 import QtWidgets

from client.client_gui import ClientMainWindow
from client.shadow_user import ShadowUser
from client.client import Client
from client.client_thread import ClientThread
from services import SelectableQueue
from log.log_config import log_config
import services

logger = log_config('chat_client', 'client.log')


@click.command()
@click.argument('address', default=services.DEFAULT_SERVER_IP)
@click.argument('port', default=services.DEFAULT_SERVER_PORT)
@click.option('--username', default='ivanov', help='username')
def start(address, port, username):

    try:
        s = socket(AF_INET, SOCK_STREAM)  # Создает сокет TCP
        s.settimeout(0.1)
        s.connect((address, port))  # Присваивает адрес и порт

        gui_app_socket, client_app_socket = socketpair()
        sq_client = SelectableQueue(gui_app_socket, client_app_socket)
        sq_gui = SelectableQueue(client_app_socket, gui_app_socket)

        client_thread_connections = (
            {'conn': s, 'events': selectors.EVENT_READ | selectors.EVENT_WRITE},
            {'conn': sq_client, 'events': selectors.EVENT_READ},
        )
        user = Client(username, '123', sq_gui=sq_gui)
        client_thread = ClientThread(user, client_thread_connections)
        client_thread.start()

        app = QtWidgets.QApplication(sys.argv)
        mw = ClientMainWindow(user, sq_gui, sq_client)
        mw.show()
        exit_code = app.exec_()

        user.close()
        client_thread.join()

        sys.exit(exit_code)

        # shadow_client = ShadowUser(sq_gui, sq_client)
        # shadow_client.start()
        #
        #
        #
        # while True:
        #
        #     command = input('Command list:\t'
        #                     'q - exit\tm - message to all:\n'
        #                     'add user to contacts - add <user>\tdel user from contacts - del <user>\tshow contacts - '
        #                     'show\n')
        #     if command == 'q':
        #         sq_gui.put('')
        #         user.close()
        #         break
        #     elif command == 'm':
        #         message = input('>> ')
        #         user.feed_data(user.send_message('#main', message))
        #         # дублируем мессагу для shadow client
        #         # sq_gui.put(user.send_message('#main', message))
        #     elif command[:3] == 'add':
        #         user.feed_data(user.add_contact(command[4:]))
        #     elif command[:3] == 'del':
        #         user.feed_data(user.del_contact(command[4:]))
        #     elif command == 'show':
        #         user.feed_data(user.get_contacts())
        #
        # client_thread.join()

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
