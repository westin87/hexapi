from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QToolBar, QLabel, QComboBox


class ModeSelectionToolbar(QToolBar):
    switch_mode = pyqtSignal(str)

    def __init__(self, network_handler):
        super().__init__("Mode selection")

        self._nh = network_handler

        mode_text = QLabel()
        mode_text.setText("Select mode:")

        self._mode_selection = QComboBox()
        self._mode_selection.setMinimumWidth(100)
        self._mode_selection.setMaximumWidth(140)
        self._mode_selection.addItem("RC")
        self._mode_selection.addItem("GPS")

        self.addWidget(mode_text)
        self.addWidget(self._mode_selection)

        self.addAction("Select", self._send_mode)

    @QtCore.pyqtSlot()
    def _send_mode(self):
        mode = self._mode_selection.currentText()
        self.switch_mode.emit(mode)

        if mode == "RC":
            command = "START_PROG_RC"
        elif mode == "GPS":
            command = "START_PROG_GPS"
        else:
            command = "START_PROG_RC"

        self._nh.send_command(command)
