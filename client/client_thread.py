import selectors
import socket
import threading

from icecream import ic

from client.client import Client
from log.log_config import log_config
from services import SelectableQueue, MessagesDeserializer, MessageProcessor

logger = log_config('client_thread', 'client.log')


class ClientThread(threading.Thread):

    def __init__(self, user: Client, connections: tuple, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.daemon = True
        self.name = f'{user.username}_Thread'
        self.user = user
        self.is_running = True

        self.sel = None

        self.connections = connections

    def run(self):
        with selectors.DefaultSelector() as self.sel:
            for conn in self.connections:
                self.sel.register(
                    conn['conn'],
                    conn['events'],
                    self._process,
                )
            self._main_loop()

    def _process(self, conn, mask):
        logger_with_name = logger.bind(server=conn.getpeername())
        if mask & selectors.EVENT_READ:
            if isinstance(conn, SelectableQueue):
                msg_list = MessagesDeserializer.recv_all(conn)
                return self.user.action_handler(msg_list)
            elif self.user.session_key:
                msg_list = MessagesDeserializer.get_messages(conn, self.user.session_key)
            else:
                msg_list = MessagesDeserializer.get_messages(conn)
            # for msg in msg_list:
                # print('===== msg ====', msg)
                # self.user.action_handler(MessageProcessor.from_msg(msg))
            if msg_list:
                self.user.action_handler(msg_list)

        if mask & selectors.EVENT_WRITE:
            data = self.user.get_data()
            try:
                if data:
                    # print('===== data =====', data, type(data))
                    if data == 'close':
                        self._close(conn)
                    else:
                        sent_size = conn.send(data)
                        if sent_size == 0:
                            logger_with_name.warning(f"can't send data to server")
                            self._close(conn)
            except Exception as e:
                logger.exception(f'Error')
                self._close(conn)

    def _main_loop(self):
        while self.is_running:
            events = self.sel.select()
            for key, mask in events:
                callback = key.data
                callback(key.fileobj, mask)

    def _close(self, conn):
        print('=========== client_thread close======')
        ic(self.user)
        self.user.feed_data(self.user.disconnect())
        self._process(conn, selectors.EVENT_WRITE)
        self.user.data_queue.join()
        for conn in self.connections:
            conn['conn'].close()
        self.is_running = False






