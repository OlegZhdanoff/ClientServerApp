from GeekChat.db.client import ClientStorage
from GeekChat.db.client_history import ClientHistoryStorage
from messages import *
from GeekChat.services import SelectableQueue


class ServerGuiProcessor:
    def __init__(self, sq_gui: SelectableQueue, session=None):
        """
        process admin messages with GUI
        :param sq_gui: Queue for admin GUI
        :param session: SQLAlchemy session
        """
        self._session = session
        self.sq_gui = sq_gui
        self.client_storage = ClientStorage(self._session)
        self.client_history_storage = None
        self.contact_storage = None

    def feed_data(self, data):
        """
        put data to Queue
        :param data: specific type of @dataclass from .messages
        """
        self.sq_gui.put(data)

    def action_handler(self, msg):
        """
        process messages from server GUI
        :param msg: specific type of @dataclass from .messages
        """
        if isinstance(msg, AdminGetUsers):
            self.feed_data(self.get_users())
        elif isinstance(msg, AdminGetHistory):
            self.feed_data(self.get_history(msg))
        elif isinstance(msg, GetContacts):
            self.feed_data(msg)

    def get_users(self):
        """
        get list of all users to admin GUI
        """
        return AdminGetUsers(users=self.client_storage.get_all())

    def get_history(self, msg: AdminGetHistory):
        """
        get login history for specific user
        :param msg: message with target username
        """
        client = self.client_storage.get_client(msg.user)
        if client:
            self.client_history_storage = ClientHistoryStorage(self._session, client)
            return AdminGetHistory(user=msg.user, history=self.client_history_storage.get_history())
