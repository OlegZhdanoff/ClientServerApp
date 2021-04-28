import selectors
import sys
from pathlib import Path

import click
from socket import *
from PyQt5 import QtWidgets

from client.client_gui import ClientMainWindow
from client.client import Client
from client.client_thread import ClientThread
from services import SelectableQueue, Config
from log.log_config import log_config
import services

logger = log_config('chat_client', 'client.log')


@click.command()
@click.argument('address', default=services.DEFAULT_SERVER_IP)
@click.argument('port', default=services.DEFAULT_SERVER_PORT)
@click.option('--username', default='ivanov', help='username')
@click.option('--password', default='123', help='password')
def start(address, port, username, password):
    """
    initialize connection and client GUI
    :param address: server IP-address
    :param port: server port
    :param username: optional username, default use credential from congiguration file
    :param password: optional user password
    """
    config_path = Path(__file__).parent.absolute() / 'client' / 'client.ini'
    try:
        config = Config(config_path)
        if address == services.DEFAULT_SERVER_IP:
            address = config.data['server']['address']
        if port == services.DEFAULT_SERVER_PORT:
            port = int(config.data['server']['port'])
        if username == 'ivanov':
            username = config.data['user']['login']
            password = config.data['user']['password']
        s = socket(AF_INET, SOCK_STREAM)
        s.settimeout(0.1)

        s.connect((address, port))  # Присваивает адрес и порт

        gui_app_socket, client_app_socket = socketpair()
        sq_client = SelectableQueue(gui_app_socket, client_app_socket)
        sq_gui = SelectableQueue(client_app_socket, gui_app_socket)

        client_thread_connections = (
            {'conn': s, 'events': selectors.EVENT_READ | selectors.EVENT_WRITE},
            {'conn': sq_client, 'events': selectors.EVENT_READ},
        )
        user = Client(username, password, sq_gui=sq_gui)
        client_thread = ClientThread(user, client_thread_connections)
        client_thread.start()

        app = QtWidgets.QApplication(sys.argv)
        mw = ClientMainWindow(user, sq_gui, sq_client, config)
        mw.show()
        exit_code = app.exec_()

        user.close()
        client_thread.join()
        sys.exit(exit_code)

    except gaierror:
        logger.exception(f'Incorrect server IP-address {address}:{port}')
    except TimeoutError:
        logger.exception(f'Wrong answer from server {address}:{port}')
    except ConnectionRefusedError:
        logger.exception(f'Server {address}:{port} is offline')
    except OSError:
        logger.exception('OS error')
    except Exception as e:
        logger.exception(f'Error connection with server {address}:{port} - {e.args}')
    finally:
        s.close()


if __name__ == '__main__':
    start()
