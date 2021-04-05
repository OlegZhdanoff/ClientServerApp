import selectors
from time import sleep

import click
import socket

from client.client import Client
from client.client_thread import ClientThread
from log.log_config import log_config
from server.server_thread import ServerThread, ServerEvents
from services import DEFAULT_SERVER_IP, DEFAULT_SERVER_PORT, LOCAL_ADMIN, LOCAL_ADMIN_PASSWORD

logger = log_config('server', 'server.log')


def run_admin(events, address, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
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
                # sleep(1)
                events.close.set()
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
    server_events = ServerEvents()
    server_thread = ServerThread(server_events, address, port)
    server_thread.start()

    run_admin(server_events, address, port)

    server_thread.join()


if __name__ == '__main__':

    start()
