from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QToolBar, QLabel, QComboBox


class ModeSelectionToolbar(QToolBar):
    switch_mode = pyqtSignal()

    def __init__(self, switch_mode_callback):
        super().__init__("Mode selection")

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

    def _send_mode(self):
        self.switch_mode.emit(self._mode_selection.currentText())
