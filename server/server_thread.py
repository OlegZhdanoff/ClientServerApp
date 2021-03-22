import selectors
import socket
import threading

from log.log_config import log_config
from server.server import ClientInstance
from services import MessagesDeserializer, MessageProcessor, LOCAL_ADMIN, PING_INTERVAL

logger = log_config('server_thread', 'server.log')


class ServerThread(threading.Thread):

    def __init__(self, conn: socket, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.daemon = True
        self.name = f'Server_Thread'
        self.is_running = True
        self.sel = None
        self.conn = conn
        self.clients = {}
        self.probe = None

    def run(self):
        with selectors.DefaultSelector() as self.sel:
            self.sel.register(
                self.conn,
                selectors.EVENT_READ,
                self._accept,
            )
            self.probe = threading.Timer(PING_INTERVAL, self.send_probe)
            self.probe.start()
            self._main_loop()

    def send_probe(self):
        for client in self.clients.values():
            client.feed_data(client.probe())
        self.probe = threading.Timer(PING_INTERVAL, self.send_probe)
        self.probe.start()

    def _accept(self, conn, mask):
        conn, addr = conn.accept()
        print(f"Клиент {conn.fileno()} {addr} подключился")
        conn.setblocking(False)
        self.sel.register(
            conn,
            selectors.EVENT_READ | selectors.EVENT_WRITE,
            self._process,
        )
        self.clients[conn] = ClientInstance(conn, addr[0])

    def _disconnect(self, conn):
        self.clients[conn].client_disconnect()
        self.sel.unregister(conn)
        conn.close()
        del self.clients[conn]

    def _process(self, conn, mask):
        logger_with_name = logger.bind(username=self.clients[conn].username, address=self.clients[conn].addr)
        if mask & selectors.EVENT_READ:
            msg_list = MessagesDeserializer.get_messages(conn)
            if msg_list:
                for msg in msg_list:
                    # debug info
                    if not msg['action'] == 'presence':
                        print(msg)

                    if not self.clients[conn].action_handler(MessageProcessor.from_msg(msg), self.clients):
                        if self.clients[conn].username == LOCAL_ADMIN:
                            self._close()
                            break
                        self._disconnect(conn)
            else:
                logger_with_name.warning(f'no data in received messages')
                self._disconnect(conn)

        if mask & selectors.EVENT_WRITE:
            if conn in self.clients.keys():
                data = self.clients[conn].get_data()
                try:
                    if data:
                        # if data == 'close' and self.clients[conn].username == DEFAULT_LOCAL_ADMIN:
                        #     self._close()
                        # else:
                        sent_size = conn.send(data)
                        if sent_size == 0:
                            logger_with_name.warning(f"can't send data to client {data}")
                            self._disconnect(conn)
                except Exception as e:
                    logger.exception(f'Error')
                    self._disconnect(conn)

    def _main_loop(self):
        while self.is_running:
            events = self.sel.select()
            for key, mask in events:
                callback = key.data
                callback(key.fileobj, mask)

    def _close(self):
        print('Server shutdown')
        self.probe.cancel()
        for conn, client in self.clients.items():
            client.data_queue.join()
            conn.close()
        self.is_running = False






