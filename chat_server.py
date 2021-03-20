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
from services import MessagesDeserializer, DEFAULT_SERVER_IP, DEFAULT_SERVER_PORT

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
    # logger.info(f"Клиент {clients[conn].username} {clients[conn].addr} отключился")
    clients[conn].client_disconnect()
    sel.unregister(conn)
    conn.close()
    del clients[conn]


def process(sel, clients, conn, mask):
    logger_with_name = logger.bind(account_name=clients[conn].username, address=clients[conn].addr)
    if mask & selectors.EVENT_READ:
        msg_list = MessagesDeserializer.get_messages(conn)
        print(msg_list)
        if msg_list:
            for msg in msg_list:
                if "action" in msg:
                    if not clients[conn].action_handler(msg['action'], msg, clients):
                        disconnect(sel, clients, conn)
        else:
            logger_with_name.warning(f'no data in received messages')
            disconnect(sel, clients, conn)

    if mask & selectors.EVENT_WRITE:
        if conn in clients.keys():
            if clients[conn].data:
                sent_size = conn.send(clients[conn].data)
                if sent_size == 0:
                    logger_with_name.warning(f"can't send data to client {clients[conn].data}")
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
@click.argument('address', default=DEFAULT_SERVER_IP)
@click.argument('port', default=DEFAULT_SERVER_PORT)
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
