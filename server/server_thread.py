import selectors
import socket
import threading
from threading import Event

from icecream import ic
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine

from db.base import Base
from db.client import ClientStorage
from db.client_history import ClientHistoryStorage

from log.log_config import log_config
from messages import GetContacts
from server.server import ClientInstance
from server.server_gui_processor import ServerGuiProcessor
from services import MessagesDeserializer, MessageProcessor, LOCAL_ADMIN, PING_INTERVAL, DEFAULT_SERVER_IP, \
    DEFAULT_SERVER_PORT, DEFAULT_DB, SelectableQueue

logger = log_config('server_thread', 'server.log')


class ServerEvents:
    def __init__(self):
        self.close = Event()


class PortProperty:
    def __init__(self, default=DEFAULT_SERVER_PORT):
        # self.name = "_" + name
        self.default = default
        self._name = None

    def __get__(self, instance, cls):
        return getattr(instance, self._name, self.default)

    def __set__(self, instance, value):
        if not isinstance(value, int):
            logger.exception(f"Port number {value} is not integer")
            raise TypeError(f"Port number {value} is not integer")
        if not 1023 < value < 65536:
            logger.exception(f"Port number {value} out of range")
            raise ValueError(f"Port number {value} out of range")
        setattr(instance, self._name, value)

    def __set_name__(self, owner, name):
        self._name = f'__{name}'


class ServerThread(threading.Thread):
    port = PortProperty()

    def __init__(self, events, sq_admin: SelectableQueue, sq_gui: SelectableQueue, address=DEFAULT_SERVER_IP,
                 port=DEFAULT_SERVER_PORT, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.daemon = True
        self.name = f'Server_Thread'
        self.is_running = True
        self.sel = None
        self.conn = None
        self.address = address
        self.port = port
        self.clients = {}
        self.probe = None
        self.events = events
        self.engine = None
        self.session = None
        self.sq_admin = sq_admin
        self.sq_gui = sq_gui
        self.server_gui_processor = None
        # self.client_storage = None
        # self.client_history_storage = None
        # self.Session = None

    def _connect_db(self, db_path=DEFAULT_DB):
        self.engine = create_engine(db_path, echo=False, pool_recycle=7200)
        Base.metadata.create_all(self.engine)
        # self.Session = scoped_session(sessionmaker(bind=self.engine))
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        self.server_gui_processor = ServerGuiProcessor(self.sq_gui, self.session)

    def run(self):
        self._connect_db()

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.conn:
                self.conn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.conn.bind((self.address, self.port))  # Присваивает адрес и порт
                self.conn.listen()  # Переходит в режим ожидания запросов;
                self.conn.setblocking(False)
                logger.info(f'Server is started on {self.address}:{self.port}')

                with selectors.DefaultSelector() as self.sel:
                    self.sel.register(
                        self.conn,
                        selectors.EVENT_READ,
                        self._accept,
                    )
                    self.sel.register(
                        self.sq_admin,
                        selectors.EVENT_READ,
                        self._process,
                    )
                    self.probe = threading.Timer(PING_INTERVAL, self.send_probe)
                    self.probe.start()
                    self._main_loop()
        except OSError:
            logger.exception('Server cannot create socket')
        finally:
            logger.info(f'Server {self.address}:{self.port} was closed ')

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
        self.clients[conn] = ClientInstance(self.session, addr[0])

    def _disconnect(self, conn):
        # self.clients[conn].client_disconnect()
        ic('======= server_thread _disconnect ======', conn, self.clients[conn])
        self.sel.unregister(conn)
        conn.close()
        del self.clients[conn]

    def _process(self, conn, mask):
        if isinstance(conn, SelectableQueue):
            username = 'GUI'
            address = ''
        else:
            username = self.clients[conn].username
            address = self.clients[conn].addr

        logger_with_name = logger.bind(username=username, address=address)

        if mask & selectors.EVENT_READ:
            if isinstance(conn, SelectableQueue):
                msg_list = MessagesDeserializer.recv_all(conn)
                return self.server_gui_processor.action_handler(msg_list)
            elif self.clients[conn].cipher_client_pk:
                msg_list = MessagesDeserializer.get_messages(conn, self.clients[conn].session_key)
            else:
                msg_list = MessagesDeserializer.get_messages(conn)
            if msg_list:
                # msg = msg_list
                # if isinstance(msg, GetContacts):
                #     self.server_gui_processor.action_handler(msg)
                # if not self.clients[conn].action_handler(msg, self.clients):
                #     self._disconnect(conn)
                for msg in msg_list:
                    # debug info
                    ic('===========server_thread _process======', msg)
                    # if not msg['action'] == 'presence':
                    #     print(msg)
                    # msg = MessageProcessor.from_msg(msg)
                    # if isinstance(msg, GetContacts):
                    #     self.server_gui_processor.action_handler(msg)
                    if not self.clients[conn].action_handler(msg, self.clients):
                        self._disconnect(conn)
            else:
                logger_with_name.warning(f'no data in received messages')
                self._disconnect(conn)

        if mask & selectors.EVENT_WRITE:
            # ic(self.clients.keys())
            # ic(conn)
            if conn in self.clients.keys():
                data = self.clients[conn].get_data()
                # ic(data)
                try:
                    if data:
                        sent_size = conn.send(data)
                        if sent_size == 0:
                            logger_with_name.warning(f"can't send data to client {data}")
                            self._disconnect(conn)
                except Exception as e:
                    logger.exception(f'Error')
                    self._disconnect(conn)

    def _main_loop(self):
        while True:
            events = self.sel.select()
            for key, mask in events:
                callback = key.data
                callback(key.fileobj, mask)
            if self.events.close.is_set():
                break
        self._close()

    def _close(self):
        print('Server shutdown')
        self.probe.cancel()
        for conn, client in self.clients.items():
            client.data_queue.join()
            conn.close()
        # self.is_running = False
        self.conn.close()






