import os
import sys
from pathlib import Path

from PyQt5 import QtWidgets, uic
from icecream import ic


class ServerMainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        ui_file_path = Path(__file__).parent.absolute() / "server_main.ui"
        # print(ui_file_path)
        # print(os.path.dirname(os.path.abspath(__file__)))
        uic.loadUi(ui_file_path, self)

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
