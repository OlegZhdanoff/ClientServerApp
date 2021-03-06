import datetime
from pathlib import Path

from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import pyqtSlot, QThread
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QListView, QWidget, QComboBox, QPushButton, QLineEdit, QToolButton, QStatusBar
from icecream import ic

from GeekChat.client.client import Client
from GeekChat.log.log_config import log_config
from GeekChat.messages import *
from GeekChat.server.server_gui import DataMonitor
from GeekChat.services import SelectableQueue, Config, STATUS

logger = log_config('client_gui', 'client.log')


class ClientMainWindow(QtWidgets.QMainWindow):
    def __init__(self, client: Client, sq_gui: SelectableQueue, sq_client: SelectableQueue, cfg: Config):
        """
        Client GUI Main window object

        :param client: Client object
        :type client: :class:`client.Client`
        :param sq_gui: Queue to receive data from Client Object
        :type sq_gui: :class:`services.SelectableQueue`
        :param sq_client: Queue to send data to Client Object
        :type sq_client: :class:`services.SelectableQueue`
        :param cfg: client configuration file
        :type cfg: :class:`services.Config`
        """
        super().__init__()
        self.client = client
        self.sq_client = sq_client
        self.monitor = DataMonitor(self, sq_gui)
        self.config = cfg
        self.logger = logger.bind(username=client.username)

        ui_file_path = Path(__file__).parent.absolute() / "client.ui"
        uic.loadUi(ui_file_path, self)

        self.profileWidget = self.findChild(QWidget, 'profileWidget')
        self.profileWidget.hide()

        self.statusComboBox = self.profileWidget.findChild(QComboBox, 'statusComboBox')
        self.statusComboBox.addItems(STATUS)
        self.statusComboBox.setEditable(False)

        self.contactList = self.findChild(QListView, 'contactList')
        self.contacts = QStandardItemModel(parent=self)
        self.contactList.clicked.connect(self.contact_selected)

        self.messagesList = self.findChild(QListView, 'messagesList')
        self.messages = {}

        self.filterUsersList = self.findChild(QListView, 'filterUsersList')
        self.filterUsers = QStandardItemModel(parent=self)
        self.filterUsersList.clicked.connect(self.is_not_contact)
        self.filterUsersList.hide()
        #
        self.search_btn = self.findChild(QPushButton, 'searchButton')
        self.search_btn.clicked.connect(self.get_filter_users)
        #
        self.search_edit = self.findChild(QLineEdit, 'searchEdit')
        self.search_edit.textChanged.connect(self.change_search)

        self.msg_edit = self.findChild(QLineEdit, 'msgEdit')
        self.msg_btn = self.findChild(QPushButton, 'msgButton')
        self.msg_btn.clicked.connect(self.send_message)

        self.add_btn = self.findChild(QToolButton, 'addButton')
        self.add_btn.clicked.connect(self.add_to_contacts)
        self.add_btn.setDisabled(True)

        self.del_btn = self.findChild(QPushButton, 'delButton')
        self.del_btn.clicked.connect(self.del_contact)
        self.del_btn.setDisabled(True)

        self.profile_btn = self.findChild(QToolButton, 'profileButton')
        self.profile_btn.clicked.connect(self.toggle_profile)
        self.login_edit = self.profileWidget.findChild(QLineEdit, 'loginEdit')
        self.password_edit = self.profileWidget.findChild(QLineEdit, 'passwordEdit')
        self.save_btn = self.profileWidget.findChild(QPushButton, 'saveButton')
        self.showInfoButton = self.profileWidget.findChild(QPushButton, 'showInfoButton')
        self.save_btn.clicked.connect(self.save_profile)
        self.showInfoButton.clicked.connect(self.toggle_login_widget)
        self.cancel_btn = self.profileWidget.findChild(QPushButton, 'cancelButton')
        self.cancel_btn.clicked.connect(self.cancel_profile)

        self.loginWidget = self.findChild(QWidget, 'loginWidget')
        self.connectButton = self.loginWidget.findChild(QPushButton, 'connectButton')
        self.connectButton.clicked.connect(self.connecting)
        self.serverMessagesList = self.loginWidget.findChild(QListView, 'serverMessagesList')
        self.serverMessages = QStandardItemModel(parent=self)
        self.serverMessagesList.setModel(self.serverMessages)

        self.statusbar = self.findChild(QStatusBar, 'statusbar')

        self.monitor.gotData.connect(self.data_handler)
        self.monitor_thread = QThread()
        self.monitor.moveToThread(self.monitor_thread)
        self.monitor_thread.started.connect(self.monitor.get_data)
        self.monitor_thread.start()

        self.load_config()

    @pyqtSlot(tuple)
    def data_handler(self, data):
        """
        process messages from server through :class:`client.Client`
        :param data: tuple with one element of any type of @dataclass from .messages
        """
        data = data[0]
        if isinstance(data, GetContacts):
            self.show_contacts(data)
        elif isinstance(data, FilterClients):
            self.show_filter_users(data.users)
        elif isinstance(data, Msg):
            self.on_msg(data)
        elif isinstance(data, Authenticate):
            self.on_auth(data)
        elif isinstance(data, Response):
            self.add_log(data.time, data.alert)

    def feed_data(self, data):
        """
        send data to Queue for :class:`client.Client`
        :param data: any type of @dataclass from .messages
        """
        self.sq_client.put(data)

    def connecting(self):
        """
        process connecting to server, send public key to server
        """
        self.connectButton.setDisabled(True)
        if not self.client.auth:
            self.client.feed_data(self.client.send_key())
            self.add_log(time.time(), f'connecting to server {self.config.data["server"]["address"]}')

    def add_log(self, tm: float, msg: str):
        """
        adding message from server to status bar and list for server messages
        :param tm: time in time() format
        :param msg: string message from server
        """
        tm = datetime.datetime.fromtimestamp(tm)
        item = QStandardItem(f'{tm.strftime("%Y-%m-%d %H:%M")} >> {msg}')
        self.serverMessages.appendRow(item)
        self.statusbar.showMessage(item.text())

    def toggle_login_widget(self):
        """
        show or hide login frame
        """
        if self.loginWidget.isHidden():
            self.loginWidget.show()
        else:
            self.loginWidget.hide()

    def on_auth(self, msg: Authenticate):
        """
        process Authenticate message from server
        :param msg: Authenticate message from server
        :type msg: :class:`messages.Authenticate`
        """
        if not msg.result:
            self.loginWidget.show()
            self.profileWidget.show()
            self.connectButton.setDisabled(False)
        else:
            self.loginWidget.hide()
            self.profileWidget.hide()
            self.connectButton.setDisabled(True)
        self.add_log(msg.time, msg.alert)

    def show_contacts(self, data: GetContacts):
        """
        show contact list received from server
        :param data: GetContacts message with list of usernames from client contact list
        :type data: :class:`messages.GetContacts`
        """
        self.contacts.clear()
        for contact in data.contacts:
            item = QStandardItem(contact)
            self.contacts.appendRow(item)
        self.contactList.setModel(self.contacts)
        self.add_log(data.time, data.action)

    def show_filter_users(self, users):
        """
        process :class:`messages.FilterClients` message from server
        :param users: filtered by mask list of users
        :type users: tuple
        """
        self.filterUsers.clear()
        for user in users:
            item = QStandardItem(user)
            self.filterUsers.appendRow(item)
        if not users:
            self.filterUsers.appendRow(QStandardItem('Not found'))
        self.filterUsersList.setModel(self.filterUsers)
        self.filterUsersList.show()
        self.add_log(time.time(), 'show filtered users')

    def get_filter_users(self):
        """
        sent to server message :class:`messages.FilterClients` with specific mask
        """
        if self.search_btn.text() == 'Close':
            self.search_btn.setText('Search')
            return self.filterUsersList.hide()
        else:
            self.search_btn.setText('Close')
        pattern = self.search_edit.text()
        if len(pattern) > 0:
            self.client.feed_data(self.client.sender(FilterClients(pattern=pattern)))

    def change_search(self):
        self.search_btn.setText('Search')

    def is_not_contact(self):
        """
        checking username for being in contact list
        """
        for item in self.filterUsersList.selectedIndexes():
            if self.contacts.findItems(item.data()):
                self.add_btn.setDisabled(True)
                return False

        self.add_btn.setDisabled(False)
        return True

    def add_to_contacts(self):
        """
        adding user to contact list
        """
        self.add_btn.setDisabled(True)
        for item in self.filterUsersList.selectedIndexes():
            self.client.feed_data(self.client.add_contact(item.data()))
            self.add_log(time.time(), f'try to add contact {item.data()}')
        self.client.feed_data(self.client.get_contacts())

    def contact_selected(self):
        """
        load chat history for selected user from contact list
        send :class:`messages.GetMessages` request to server if local history is not exists
        :return:
        """
        if self.contactList.selectedIndexes():
            contact = self.contactList.selectedIndexes()[0].data()
            if self.is_contact(contact):
                if not self.messages.get(contact):
                    self.messages.setdefault(contact, QStandardItemModel(parent=self))
                    tm = datetime.datetime(2000, 1, 1, 0, 0)
                    self.client.feed_data(self.client.get_messages(tm.timestamp(), contact))
                self.messagesList.setModel(self.messages[contact])
            ic(self.messages[contact])

    def is_contact(self, contact):
        # for item in self.contactList.selectedIndexes():
        if not contact:
            self.del_btn.setDisabled(True)
            return False

        self.del_btn.setDisabled(False)
        return True

    def del_contact(self):
        """
        delete user from contact list
        send :class:`messages.DelContact` request to server
        """
        self.del_btn.setDisabled(True)
        for item in self.contactList.selectedIndexes():
            self.client.feed_data(self.client.del_contact(item.data()))
            self.add_log(time.time(), f'try to delete contact {item.data()}')
        self.client.feed_data(self.client.get_contacts())

    def send_message(self):
        """
        send message :class:`messages.Msg` to server
        """
        text = self.msg_edit.text()
        self.msg_edit.setText('')
        recipient = self.contactList.currentIndex().data()
        if text and recipient:
            self.client.feed_data(self.client.send_message(recipient, text))
            self.update_chat(recipient, self.client.username, datetime.datetime.now(), text)

    def on_msg(self, msg: Msg):
        """
        process :class:`messages.Msg` message received from server
        adding this message to appropriate chat
        :param msg: message received from server
        :type msg: :class:`messages.Msg`
        """
        tm = datetime.datetime.fromtimestamp(msg.time)
        if msg.from_ == self.client.username:
            self.update_chat(msg.to, msg.from_, tm, msg.text)
        else:
            self.update_chat(msg.from_, msg.from_, tm, msg.text)
        ic(msg)

    def update_chat(self, contact, sender, tm, text):
        """
        update selected chat with new message
        :param contact: username from contact list
        :param sender: message sender username
        :param tm: time in time() format
        :param text: message body
        """
        if not self.messages.get(contact):
            self.messages.setdefault(contact, QStandardItemModel(parent=self))
        item = QStandardItem(f'{tm.strftime("%Y-%m-%d %H:%M")} {sender} >> {text}')
        self.messages[contact].appendRow(item)

    def load_config(self):
        """
        load data from configuration file
        """
        self.login_edit.setText(self.config.data['user']['login'])
        self.password_edit.setText(self.config.data['user']['password'])
        status_idx = self.statusComboBox.findText(self.config.data['user']['status'])
        if status_idx > -1:
            self.statusComboBox.setCurrentIndex(status_idx)
        else:
            self.add_log(time.time(), f"wrong status in config - {self.config.data['user']['status']}")
            self.logger.warning(f"wrong status in config - {self.config.data['user']['status']}")

    def cancel_profile(self):
        """
        cancel changes in profile and loading data from configuration file
        """
        self.load_config()
        self.toggle_profile()

    def toggle_profile(self):
        """
        show or hide profile frame
        """
        if self.profileWidget.isHidden():
            self.profileWidget.show()
        else:
            self.profileWidget.hide()

    def save_profile(self):
        """
        save new profile data to configuration file and hide profile frame
        """
        self.config.data['user']['login'] = self.login_edit.text()
        self.client.username = self.login_edit.text()
        self.config.data['user']['password'] = self.password_edit.text()
        self.client.password = self.password_edit.text()
        self.config.data['user']['status'] = self.statusComboBox.currentText()
        self.client.status = self.statusComboBox.currentText()
        self.config.save_config()
        self.add_log(time.time(), 'config file saved')
        self.toggle_profile()

    def closeEvent(self, *args, **kwargs):
        """
        closing main window
        """
        ic('========== closing ==================')
        self.monitor_thread.quit()
        self.monitor_thread.disconnect()
        self.monitor_thread.exit(0)
        self.monitor.disconnect()
