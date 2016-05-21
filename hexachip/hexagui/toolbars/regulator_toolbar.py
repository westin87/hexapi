from PyQt5 import QtCore
from PyQt5.QtWidgets import QToolBar, QLabel, QLineEdit

from hexacommon.constants import REGULATOR


class RegulatorToolbar(QToolBar):
    def __init__(self, network_handler):
        super().__init__("Regulator Settings")

        self._nh = network_handler

        self.addWidget(QLabel("Speed K"))
        self._speed_k = self._create_text_edit(str(REGULATOR.SPEED_K))
        self.addWidget(self._speed_k)

        self.addWidget(QLabel("Speed Td"))
        self._speed_td = self._create_text_edit(str(REGULATOR.SPEED_TD))
        self.addWidget(self._speed_td)

        self.addAction("Update regulators", self._update_regulators)

    @QtCore.pyqtSlot()
    def _update_regulators(self):
        self._nh.send_command("SET_REG_PARAMS",
                              self._speed_k.text(), self._speed_td.text())

    @staticmethod
    def _create_text_edit(placeholder_text):
        edit = QLineEdit()

        edit.setMinimumWidth(80)
        edit.setMaximumWidth(100)

        edit.setAlignment(QtCore.Qt.AlignRight)
        edit.setPlaceholderText(placeholder_text)

        return edit
