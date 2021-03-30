import selectors

import click
import socket

from client.client import Client
from client.client_thread import ClientThread
from log.log_config import log_config
from server.server_thread import ServerThread
from services import DEFAULT_SERVER_IP, DEFAULT_SERVER_PORT, LOCAL_ADMIN, LOCAL_ADMIN_PASSWORD

logger = log_config('server', 'server.log')


def run_admin(address, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.1)
        s.connect((address, port))
        admin = Client(LOCAL_ADMIN, LOCAL_ADMIN_PASSWORD, 'online')
        client_thread_connections = (
            {'conn': s, 'events': selectors.EVENT_READ | selectors.EVENT_WRITE},
        )
        admin_thread = ClientThread(admin, client_thread_connections)
        admin_thread.start()

        admin.feed_data(admin.authenticate())

        while True:

            command = input('Command list:\t'
                            'q - server shutdown\tm - message to all:\t')
            if command == 'q':
                admin.close()
                break
            elif command == 'm':
                message = input('>> ')
                admin.feed_data(admin.send_message('#main', message))

        admin_thread.join()


@click.command()
@click.argument('address', default=DEFAULT_SERVER_IP)
@click.argument('port', default=DEFAULT_SERVER_PORT)
def start(address, port):
    print(address, port)
    server_thread = ServerThread(address, port)
    server_thread.start()

    run_admin(address, port)

    server_thread.join()

    # try:
    #     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    #         s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #         s.bind((address, port))  # Присваивает адрес и порт
    #         s.listen()  # Переходит в режим ожидания запросов;
    #         s.setblocking(False)
    #         logger.info(f'Server is started on {address}:{port}')
    #
    #         server_thread = ServerThread(s)
    #         server_thread.start()
    #
    #         run_admin(address, port)
    #
    #         server_thread.join()
    #
    # except OSError:
    #     logger.exception('Server cannot create socket')
    # finally:
    #     logger.info(f'Server {address}:{port} was closed ')


if __name__ == '__main__':

    start()
