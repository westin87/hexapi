from PyQt5 import QtCore
from PyQt5.QtWidgets import QToolBar, QLabel, QLineEdit


class RegulatorToolbar(QToolBar):
    def __init__(self, network_handler):
        super().__init__("Regulator Settings")

        self._nh = network_handler

        self.addWidget(QLabel("Yaw K"))
        self._yaw_k = self._create_text_edit("0.5")
        self.addWidget(self._yaw_k)

        self.addWidget(QLabel("Yaw Td"))
        self._yaw_td = self._create_text_edit("0.1")
        self.addWidget(self._yaw_td)

        self.addWidget(QLabel("Pitch K"))
        self._pitch_k = self._create_text_edit("12")
        self.addWidget(self._pitch_k)

        self.addWidget(QLabel("Pitch Td"))
        self._pitch_td = self._create_text_edit("4")
        self.addWidget(self._pitch_td)

        self.addAction("Update regulators", self._update_regulators)

    @QtCore.pyqtSlot()
    def _update_regulators(self):
        self._nh.send_command("SET_REG_PARAMS",
                              self._yaw_k, self._yaw_td,
                              self._pitch_k, self._pitch_td)

    @staticmethod
    def _create_text_edit(placeholder_text):
        edit = QLineEdit()

        edit.setMinimumWidth(80)
        edit.setMaximumWidth(100)

        edit.setAlignment(QtCore.Qt.AlignRight)
        edit.setPlaceholderText(placeholder_text)

        return edit
