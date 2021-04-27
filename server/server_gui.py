from pathlib import Path

from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QThread, QSortFilterProxyModel, Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QListView, QTableView, QLineEdit

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
        self.filter_users = QSortFilterProxyModel(self)
        self.filter_users.setSourceModel(self.users)
        self.filter_users.sort(0, Qt.AscendingOrder)
        self.filter_users.setFilterKeyColumn(0)

        self.filterEdit = self.findChild(QLineEdit, 'filterEdit')
        self.filterEdit.textChanged.connect(self.set_filter)

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
        elif isinstance(data, GetContacts):
            self.on_login(data)

    def feed_data(self, data):
        self.sq_admin.put(data)

    def show_users(self, data):
        self.users.clear()
        for user in data.users:
            item = QStandardItem(user[0])
            self.users.appendRow(item)
        self.userList.setModel(self.filter_users)

    def get_history(self, item):
        self.feed_data(AdminGetHistory(user=item.data()))

    def show_history(self, data):
        self.history.clear()
        for row in data.history:
            items = [QStandardItem(item) for item in row]
            self.history.appendRow(items)
        self.historyTable.setModel(self.history)
        self.historyTable.resizeColumnsToContents()

    def set_filter(self, text):
        self.filter_users.setFilterFixedString(text)

    def on_login(self, data: GetContacts):
        users = self.users.findItems(data.login)
        if not users:
            return self.feed_data(AdminGetUsers())
        if data.login == self.userList.currentIndex().data():
            self.feed_data(AdminGetHistory(user=data.login))
