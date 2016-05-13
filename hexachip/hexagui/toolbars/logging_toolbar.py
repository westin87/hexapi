from PyQt5 import QtCore
from PyQt5.QtWidgets import QToolBar, QLabel, QLineEdit


class LoggingToolbar(QToolBar):
    def __init__(self, network_handler):
        super().__init__("Logging Control")

        self._nh = network_handler

        file_tag = QLabel()
        file_tag.setText("Log file tag:")

        self._tag_edit = QLineEdit()
        self._tag_edit.setMinimumWidth(100)
        self._tag_edit.setMaximumWidth(140)
        self._tag_edit.setAlignment(QtCore.Qt.AlignRight)

        self.addWidget(file_tag)
        self.addWidget(self._tag_edit)
        self.addAction("Start logging", self._start_logging)
        self.addAction("Stop logging", self._stop_logging)

    @QtCore.pyqtSlot()
    def _start_logging(self):
        file_tag = self._tag_edit.text()
        self._nh.send_command("START_LOGGING", file_tag)

    @QtCore.pyqtSlot()
    def _stop_logging(self):
        self._nh.send_command("STOP_LOGGING")
