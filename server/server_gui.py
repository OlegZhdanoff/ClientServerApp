import os
import sys
from pathlib import Path

from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QThread
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QListView, QTableView
from icecream import ic

from messages import *
from services import SelectableQueue


class DataMonitor(QObject):
    gotData = pyqtSignal(tuple)

    def __init__(self, parent, sq_gui: SelectableQueue):
        super().__init__()
        self.parent = parent
        self.sq_gui = sq_gui

    def get_data(self):
        while True:
            data = self.sq_gui.get()
            # print('DataMonitor ========== ',data)
            self.gotData.emit((data,))
            self.sq_gui.task_done()


class ServerMainWindow(QtWidgets.QMainWindow):
    def __init__(self, sq_gui: SelectableQueue, sq_admin: SelectableQueue):
        super().__init__()
        self.sq_admin = sq_admin
        self.monitor = DataMonitor(self, sq_gui)

        # self.sq_admin.put
        # self.sq_gui.get

        ui_file_path = Path(__file__).parent.absolute() / "server_main.ui"
        uic.loadUi(ui_file_path, self)

        self.userList = self.findChild(QListView, 'userList')
        self.users = QStandardItemModel(parent=self)
        self.userList.clicked.connect(self.get_history)

        self.historyTable = self.findChild(QTableView, 'historyTable')
        self.history = QStandardItemModel(parent=self)
        self.history.setHorizontalHeaderLabels(('login', 'ip_address', 'time'))
        self.feed_data(AdminGetUsers())

        self.monitor.gotData.connect(self.data_handler)

        self.monitor_thread = QThread()
        self.monitor.moveToThread(self.monitor_thread)
        self.monitor_thread.started.connect(self.monitor.get_data)
        self.monitor_thread.start()

    @pyqtSlot(tuple)
    def data_handler(self, data):
        data = data[0]
        if isinstance(data, AdminGetUsers):
            self.show_users(data)
        elif isinstance(data, AdminGetHistory):
            self.show_history(data)

    def feed_data(self, data):
        self.sq_admin.put(data)

    def show_users(self, data):
        # print(data.users)
        for user in data.users:
            item = QStandardItem(user[0])
            self.users.appendRow(item)
        self.userList.setModel(self.users)

    def get_history(self):
        idx = self.userList.currentIndex()
        # print(idx.data())
        self.feed_data(AdminGetHistory(user=idx.data()))

    def show_history(self, data):
        # print(data)
        for row in data.history:
            items = [QStandardItem(item) for item in row]
            self.history.appendRow(items)
        self.historyTable.setModel(self.history)
        self.historyTable.resizeColumnsToContents()
