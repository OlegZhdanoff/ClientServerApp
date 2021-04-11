import os
import sys
from pathlib import Path

from PyQt5 import QtWidgets, uic
from icecream import ic

from services import SelectableQueue


class ServerMainWindow(QtWidgets.QMainWindow):
    def __init__(self, sq_gui: SelectableQueue,  sq_client: SelectableQueue):
        super().__init__()
        self.sq_gui = sq_gui
        self.sq_client = sq_client

        # self.sq_client.put
        # self.sq_gui.get

        ui_file_path = Path(__file__).parent.absolute() / "server_main.ui"
        # print(ui_file_path)
        # print(os.path.dirname(os.path.abspath(__file__)))
        uic.loadUi(ui_file_path, self)
        self.centralWidget().userList.clicked.connect()
        # self.btnQuit.clicked.connect(QtWidgets.qApp.quit)
        # self.textEdit.textChanged.connect(self.on_text_changed)

    def on_text_changed(self):
        # ic(self.textEdit.toPlainText())
        pass


if __name__ == "__main__":
    # setup_plugin_path()

    app = QtWidgets.QApplication(sys.argv)

    mw = ServerMainWindow()
    mw.show()
    sys.exit(app.exec_())
