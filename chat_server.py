import selectors
import sys
import time
import click
import socket

from PyQt5 import QtWidgets
from icecream import ic

from client.client import Client
from client.client_thread import ClientThread
from log.log_config import log_config
from server.server_gui import ServerMainWindow
from server.server_thread import ServerThread, ServerEvents
from services import DEFAULT_SERVER_IP, DEFAULT_SERVER_PORT, LOCAL_ADMIN, LOCAL_ADMIN_PASSWORD, SelectableQueue

logger = log_config('server', 'server.log')


def run_admin(events, address, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.1)
        s.connect((address, port))
        admin = Client(LOCAL_ADMIN, LOCAL_ADMIN_PASSWORD, 'online')
        client_thread_connections = (
            {'conn': s, 'events': selectors.EVENT_READ | selectors.EVENT_WRITE},
            # {'conn': sq_admin, 'events': selectors.EVENT_READ},
        )
        admin_thread = ClientThread(admin, client_thread_connections)
        admin_thread.start()
        admin.feed_data(admin.authenticate())

        admin.close()
        admin_thread.join()
        return admin


@click.command()
@click.argument('address', default=DEFAULT_SERVER_IP)
@click.argument('port', default=DEFAULT_SERVER_PORT)
def start(address, port):
    """
    start server application
    initialize Queues for backend and GUI
    create backed server thread
    initialize GUI
    :param address: server IP-address
    :param port: server port
    """
    print(address, port)
    server_events = ServerEvents()

    gui_app_socket, client_app_socket = socket.socketpair()
    sq_admin = SelectableQueue(gui_app_socket, client_app_socket)
    sq_gui = SelectableQueue(client_app_socket, gui_app_socket)

    server_thread = ServerThread(server_events, sq_admin, sq_gui, address, port)
    server_thread.start()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        time.sleep(1)
        s.settimeout(0.2)
        s.connect((address, port))
        admin = Client(LOCAL_ADMIN, LOCAL_ADMIN_PASSWORD, 'online')

        client_thread_connections = (
            {'conn': s, 'events': selectors.EVENT_READ | selectors.EVENT_WRITE},
        )
        admin_thread = ClientThread(admin, client_thread_connections)
        admin_thread.start()
        admin.feed_data(admin.send_key())

        app = QtWidgets.QApplication(sys.argv)
        mw = ServerMainWindow(sq_gui, sq_admin)
        mw.show()
        exit_code = app.exec_()

        admin.close()
        admin_thread.join()

        server_events.close.set()
        ic('=============server closing =====================')
        server_thread.join()
        sys.exit(exit_code)


if __name__ == '__main__':

    start()
