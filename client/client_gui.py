import os
import sys
from pathlib import Path

from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QThread
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QListView, QTableView, QWidget, QComboBox

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
        elif isinstance(data, Authenticate):
            if data.result:
                self.client.auth = True
                print('online')
                self.client.status = 'online'
                self.client.feed_data(self.client.get_contacts())

    def feed_data(self, data):
        self.sq_client.put(data)

    def show_contacts(self, data):
        # print(data.contacts)
        self.contacts.clear()
        for contact in data.contacts:
            item = QStandardItem(contact[0])
            self.contacts.appendRow(item)
        self.contactList.setModel(self.contacts)
