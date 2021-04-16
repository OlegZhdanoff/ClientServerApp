import os
import sys
from pathlib import Path

from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QThread, QStringListModel, QModelIndex
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QListView, QTableView, QWidget, QComboBox, QPushButton, QLineEdit, QToolButton
from icecream import ic

from client.client import Client
from messages import *
from server.server_gui import DataMonitor
from services import SelectableQueue


class ClientMainWindow(QtWidgets.QMainWindow):
    def __init__(self, client: Client, sq_gui: SelectableQueue, sq_client: SelectableQueue):
        super().__init__()
        self.client = client
        self.sq_client = sq_client
        self.monitor = DataMonitor(self, sq_gui)

        self.client.feed_data(client.authenticate())

        ui_file_path = Path(__file__).parent.absolute() / "client.ui"
        uic.loadUi(ui_file_path, self)

        self.profileWidget = self.findChild(QWidget, 'profileWidget')
        self.profileWidget.hide()

        self.statusComboBox = self.profileWidget.findChild(QComboBox, 'statusComboBox')

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

        self.monitor.gotData.connect(self.data_handler)
        self.monitor_thread = QThread()
        self.monitor.moveToThread(self.monitor_thread)
        self.monitor_thread.started.connect(self.monitor.get_data)
        self.monitor_thread.start()

    @pyqtSlot(tuple)
    def data_handler(self, data):
        data = data[0]
        if isinstance(data, GetContacts):
            self.show_contacts(data)
        elif isinstance(data, FilterClients):
            self.show_filter_users(data.users)
        elif isinstance(data, Msg):
            self.on_msg(data)

    def feed_data(self, data):
        self.sq_client.put(data)

    def show_contacts(self, data):
        self.contacts.clear()
        for contact in data.contacts:
            item = QStandardItem(contact)
            self.contacts.appendRow(item)
        self.contactList.setModel(self.contacts)

    def show_filter_users(self, users):
        self.filterUsers.clear()
        for user in users:
            item = QStandardItem(user)
            self.filterUsers.appendRow(item)
        if not users:
            self.filterUsers.appendRow(QStandardItem('Not found'))
        self.filterUsersList.setModel(self.filterUsers)
        self.filterUsersList.show()

    def get_filter_users(self):
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
        for item in self.filterUsersList.selectedIndexes():
            if self.contacts.findItems(item.data()):
                self.add_btn.setDisabled(True)
                return False

        self.add_btn.setDisabled(False)
        return True

    def add_to_contacts(self):
        self.add_btn.setDisabled(True)
        for item in self.filterUsersList.selectedIndexes():
            self.client.feed_data(self.client.add_contact(item.data()))
        self.client.feed_data(self.client.get_contacts())

    def contact_selected(self):
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
        self.del_btn.setDisabled(True)
        for item in self.contactList.selectedIndexes():
            self.client.feed_data(self.client.del_contact(item.data()))
        self.client.feed_data(self.client.get_contacts())

    def send_message(self):
        text = self.msg_edit.text()
        self.msg_edit.setText('')
        recipient = self.contactList.currentIndex().data()
        if text and recipient:
            self.client.feed_data(self.client.send_message(recipient, text))
            self.update_chat(recipient, self.client.username, datetime.datetime.now(), text)

    def on_msg(self, msg: Msg):
        tm = datetime.datetime.fromtimestamp(msg.time)
        if msg.from_ == self.client.username:
            self.update_chat(msg.to, msg.from_, tm, msg.text)
        else:
            self.update_chat(msg.from_, msg.from_, tm, msg.text)
        ic(msg)

    def update_chat(self, contact, sender, tm, text):
        if not self.messages.get(contact):
            self.messages.setdefault(contact, QStandardItemModel(parent=self))
        item = QStandardItem(f'{tm.strftime("%Y-%m-%d %H:%M")} {sender} >> {text}')
        self.messages[contact].appendRow(item)
