import logging
from PyQt5 import QtCore
from PyQt5.QtWidgets import QToolBar, QLabel, QLineEdit


class NetworkToolbar(QToolBar):
    def __init__(self, network_handler, reset_callback):

        super().__init__("Network")

        self._nh = network_handler
        self._reset_gui = reset_callback

        self._connected = False
        ping_timer = QtCore.QTimer(self)
        ping_timer.timeout.connect(self._send_ping)
        ping_timer.start(500)

        host_text = QLabel("Connect to hexapi:")

        self._host_edit = QLineEdit()
        self._host_edit.setMinimumWidth(100)
        self._host_edit.setMaximumWidth(140)
        self._host_edit.setAlignment(QtCore.Qt.AlignRight)
        self._host_edit.setPlaceholderText("192.169.1.2")

        self.addWidget(host_text)
        self.addWidget(self._host_edit)

        self.addAction("Set host", self._connect)
        self.addAction("Land", self._land)
        self.addAction("Kill!", self._kill)

    def _connect(self):
        logging.info("MA: Setting host")
        self._connected = True
        host_and_port = self._host_edit.text().split(":")

        if len(host_and_port) == 2:
            port = int(host_and_port[1])
        else:
            port = 4092

        self._nh.set_host(host_and_port[0], port)

    def _send_ping(self):
        if self._connected:
            self._nh.send_command("PING")

        self._reset_gui()

    def _land(self):
        self._nh.send_command("LAND")

        self._reset_gui()

    def _kill(self):
        self._nh.send_command("KILL")

        self._reset_gui()
