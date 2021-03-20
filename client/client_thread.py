import json
import queue
import selectors
import socket
import threading

from client.client import Client
from log.log_config import log_config
from services import SelectableQueue, MessagesDeserializer

logger = log_config('client_thread', 'client.log')


class ClientThread(threading.Thread):

    def __init__(self, user: Client, connections: tuple, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.daemon = True
        self.name = f'{user.account_name}_Thread'
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
    #
    # def _process_gui(self, conn, mask):
    #     logger_with_name = logger.bind(server=conn.getpeername())
    #     if mask & selectors.EVENT_READ:
    #         print('SelectableQueue', conn)
    #         data = conn.get()
    #         if data:
    #             data = data.decode(settings.ENCODING)
    #             print('data', data)
    #             msg_list = settings.get_msg_list(data)
    #             if msg_list:
    #                 for data in msg_list:
    #                     msg = json.loads(data)
    #                     if "action" in msg:
    #                         self.user.action_handler(msg["action"], msg)
    #                     elif "response" in msg:
    #                         self.user.response_processor(msg["response"], msg)

    def _process(self, conn, mask):
        logger_with_name = logger.bind(server=conn.getpeername())
        if mask & selectors.EVENT_READ:
            msg_list = MessagesDeserializer.get_messages(conn)
            if msg_list:
                for msg in msg_list:
                    # msg = json.loads(data)
                    if "action" in msg:
                        self.user.action_handler(msg["action"], msg)
                    elif "response" in msg:
                        self.user.response_processor(msg["response"], msg)

        if mask & selectors.EVENT_WRITE:
            try:
                data = self.user.data_queue.get_nowait()
                # print('data', data)
                if data:
                    sent_size = conn.send(data)
                    # print(conn)
                    if sent_size == 0:
                        logger_with_name.warning(f"can't send data to server")
                        self.user.data_queue.task_done()
                        return
                    self.user.data_queue.task_done()
                else:
                    # print('tasks=', self.user.data_queue.unfinished_tasks)
                    self.user.data_queue.task_done()
                    # print('2tasks=', self.user.data_queue.unfinished_tasks)
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
        for conn in self.connections:
            conn['conn'].close()
        self.is_running = False






