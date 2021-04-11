from db.client import ClientStorage
from db.client_history import ClientHistoryStorage
from messages import *
from services import SelectableQueue


class ServerGuiProcessor:
    def __init__(self, sq_gui: SelectableQueue, session=None):
        self._session = session
        self.sq_gui = sq_gui
        self.client_storage = ClientStorage(self._session)
        self.client_history_storage = None
        self.contact_storage = None

    def feed_data(self, data):
        self.sq_gui.put(data)

    def action_handler(self, msg):
        if isinstance(msg, AdminGetUsers):
            self.feed_data(self.get_users())
        elif isinstance(msg, AdminGetHistory):
            self.feed_data(self.get_history(msg))

    def get_users(self):
        return AdminGetUsers(users=self.client_storage.get_all())

    def get_history(self, msg):
        client = self.client_storage.get_client(msg.user)
        if client:
            self.client_history_storage = ClientHistoryStorage(self._session, client)
            return AdminGetHistory(history=self.client_history_storage.get_history())
