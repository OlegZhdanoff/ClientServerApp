import json
import queue
import selectors
import socket
import threading
import select

import settings
from client.client import Client
from log.log_config import log_config

logger = log_config('client_thread', 'client.log')


class SelectableQueue(queue.Queue):
    def __init__(self, put_socket, get_socket, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._put_socket = put_socket
        self._get_socket = get_socket

    def fileno(self):
        return self._get_socket.fileno()

    def getpeername(self):
        return self._get_socket.getpeername()

    def put(self, item, *args, **kwargs):
        super().put(item, *args, **kwargs)
        self._put_socket.send(b'x')

    def get(self, *args, **kwargs):
        self._get_socket.recv(1)
        return super().get(*args, **kwargs)

    def is_not_empty(self):
        return not super().empty()

    def close(self):
        self._get_socket.close()
        self._put_socket.close()

# pq1 = SelectableQueue()
# pq2 = SelectableQueue()

#
# def TimerHandler():
#     print("hello, world")
#     # pq1.put('1')
#     # pq2.put('2')
#
#     t = threading.Timer(2.0, TimerHandler)
#     t.start()
#
#
# def TestPoolableQueue():
#     t = threading.Timer(2.0, TimerHandler)
#     t.start()

    # while True:
    #     print('.')
    #     r, w, e = select.select([pq1, pq2], [], [])
    #     for handle in r:
    #         print(handle.get())
    #         handle.task_done()


class ClientThread(threading.Thread):

    def __init__(self, sock: socket, user: Client, sq_gui: SelectableQueue, sq_client: SelectableQueue, *args,
                 **kwargs):
        super().__init__(*args, **kwargs)

        self.daemon = True
        self.name = f'{user.account_name}_Thread'
        self.sock = sock
        self.user = user
        self.sq_gui = sq_gui
        self.sq_client = sq_client
        self.is_running = True

        self.sel = None

    def run(self):
        self.user.feed_data(self.user.authenticate())

        with selectors.DefaultSelector() as self.sel:
            self.sel.register(
                self.sock,
                selectors.EVENT_READ | selectors.EVENT_WRITE,
                lambda conn, mask: self._process(conn, mask),
            )

            self.sel.register(
                self.sq_gui,
                selectors.EVENT_READ | selectors.EVENT_WRITE,
                lambda conn, mask: self._process_gui(conn, mask),
            )

            self.sel.register(
                self.sq_client,
                selectors.EVENT_READ | selectors.EVENT_WRITE,
                lambda conn, mask: self._process_gui(conn, mask),
            )

            self._main_loop()

    def _process_gui(self, conn, mask):
        pass

    def _process(self, conn, mask):
        logger_with_name = logger.bind(server=conn.getpeername())
        if mask & selectors.EVENT_READ:
            data = settings.recv_all(conn)
            msg_list = settings.get_msg_list(data)
            if msg_list:
                for data in msg_list:
                    msg = json.loads(data)
                    if "action" in msg:
                        self.user.action_handler(msg["action"], msg)
                    elif "response" in msg:
                        self.user.response_processor(msg["response"], msg)

        if mask & selectors.EVENT_WRITE:
            try:
                data = self.user.data_queue.get_nowait()
                print('data', data)
                if data:
                    sent_size = conn.send(data)
                    if sent_size == 0:
                        logger_with_name.warning(f"can't send data to server")
                        self.user.data_queue.task_done()
                        return
                    self.user.data_queue.task_done()
                else:
                    print('tasks=', self.user.data_queue.unfinished_tasks)
                    self.user.data_queue.task_done()
                    print('2tasks=', self.user.data_queue.unfinished_tasks)
                    self._close(conn)

            except queue.Empty as e:
                pass
            except Exception as e:
                logger.exception(f'Error')
                # self.user.data_queue.task_done()
                self._close(conn)

    def _main_loop(self):
        while self.is_running:
            events = self.sel.select()
            for key, mask in events:
                callback = key.data
                callback(key.fileobj, mask)

    def _close(self, conn):
        self.user.feed_data(self.user.disconnect())
        self._process(conn, selectors.EVENT_WRITE)
        self.user.data_queue.join()
        self.sel.unregister(conn)
        self.sq_gui.close()
        self.sq_client.close()
        conn.close()
        self.is_running = False






