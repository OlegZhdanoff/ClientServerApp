import click
import socket

from log.log_config import log_config
from server.server_thread import ServerThread
from services import DEFAULT_SERVER_IP, DEFAULT_SERVER_PORT

logger = log_config('server', 'server.log')


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
            logger.info(f'Server is started on {address}:{port}')

            server_thread = ServerThread(s)
            server_thread.start()
            server_thread.join()

    except OSError:
        logger.exception('Server cannot create socket')
    finally:
        logger.info(f'Server {address}:{port} was closed ')


if __name__ == '__main__':

    start()
