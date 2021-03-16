import errno
import json
import structlog
import click
import socket
import time
from contextlib import closing
import selectors

from server.server import Server
from log.log_config import log_config
import settings

logger = log_config('server', 'server.log')


def accept(sel, clients, sock, _):
    conn, addr = sock.accept()
    print(f"Клиент {conn.fileno()} {addr} подключился")
    conn.setblocking(False)
    sel.register(
        conn,
        selectors.EVENT_READ | selectors.EVENT_WRITE,
        lambda conn, mask: process(sel, clients, conn, mask),
    )
    clients[conn] = Server(conn, addr[0])


def disconnect(sel, clients, conn):
    print(f"Клиент {clients[conn].username} {clients[conn].addr} отключился")
    sel.unregister(conn)
    conn.close()
    del clients[conn]


def process(sel, clients, conn, mask):
    if mask & selectors.EVENT_READ:
        data = settings.recv_all(conn)
        msg_list = settings.get_msg_list(data)
        if msg_list:
            for data in msg_list:
                msg = json.loads(data)
                if "action" in msg:
                    if not clients[conn].action_handler(msg['action'], msg, clients):
                        disconnect(sel, clients, conn)
        else:
            disconnect(sel, clients, conn)

    if mask & selectors.EVENT_WRITE:
        if conn in clients.keys():
            if clients[conn].data:
                sent_size = conn.send(clients[conn].data)
                if sent_size == 0:
                    disconnect(sel, clients, conn)
                    return
                clients[conn].data = clients[conn].data[sent_size:]


def main_loop(sel):
    while True:
        events = sel.select()
        for key, mask in events:
            callback = key.data
            callback(key.fileobj, mask)


@click.command()
@click.argument('address', default=settings.DEFAULT_SERVER_IP)
@click.argument('port', default=settings.DEFAULT_SERVER_PORT)
def start(address, port):
    print(address, port)
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((address, port))  # Присваивает адрес и порт
            s.listen()  # Переходит в режим ожидания запросов;
            s.setblocking(False)
            # ci = Server()
            logger.info(f'Server is started on {address}:{port}')
            clients = {}
            with selectors.DefaultSelector() as sel:
                sel.register(
                    s,
                    selectors.EVENT_READ,
                    lambda conn, mask: accept(sel, clients, conn, mask),
                )

                main_loop(sel)

    except OSError:
        logger.exception('Server cannot create socket')
    finally:
        logger.info(f'Server {address}:{port} was closed ')


if __name__ == '__main__':

    start()
