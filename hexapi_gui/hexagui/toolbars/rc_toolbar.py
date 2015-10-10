from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QMessageBox, QToolBar, QGridLayout, QPushButton, \
    QWidget, QLabel


class RemoteControlToolbar(QToolBar):
    start_motors = pyqtSignal()
    set_auto_return = pyqtSignal(bool)

    def __init__(self):
        super().__init__("RC Control Values")

        layout = QGridLayout()

        self._auto_return = False

        pitch_static_text = _create_text("Pitch:", Qt.AlignLeft)
        self._pitch_value_text = _create_text("0", Qt.AlignRight)

        roll_static_text = _create_text("Roll:", Qt.AlignLeft)
        self._roll_value_text = _create_text("0", Qt.AlignRight)

        yaw_static_text = _create_text("Yaw:", Qt.AlignLeft)
        self._yaw_value_text = _create_text("0", Qt.AlignRight)

        altitude_static_text = _create_text("Altitude:", Qt.AlignLeft)
        self._altitude_value_text = _create_text("0", Qt.AlignRight)

        mode_static_text = _create_text("Mode:", Qt.AlignLeft)
        self._mode_value_text = _create_text("0", Qt.AlignRight)

        self._auto_return_button = QPushButton("Auto return")
        self._auto_return_button.clicked.connect(self._set_auto_return)

        start_button = QPushButton("Start motors")
        start_button.clicked.connect(self.start_motors)

        help_button = QPushButton("Show RC help")
        help_button.clicked.connect(self._show_rc_help)

        layout.addWidget(pitch_static_text, 0, 0, 1, 1,
                         Qt.AlignVCenter)
        layout.addWidget(self._pitch_value_text, 0, 1, 1, 1,
                         Qt.AlignVCenter)

        layout.addWidget(roll_static_text, 1, 0, 1, 1,
                         Qt.AlignVCenter)
        layout.addWidget(self._roll_value_text, 1, 1, 1, 1,
                         Qt.AlignVCenter)

        layout.addWidget(yaw_static_text, 2, 0, 1, 1,
                         Qt.AlignVCenter)
        layout.addWidget(self._yaw_value_text, 2, 1, 1, 1,
                         Qt.AlignVCenter)

        layout.addWidget(altitude_static_text, 3, 0, 1, 1,
                         Qt.AlignVCenter)
        layout.addWidget(self._altitude_value_text, 3, 1, 1, 1,
                         Qt.AlignVCenter)

        layout.addWidget(mode_static_text, 4, 0, 1, 1,
                         Qt.AlignVCenter)
        layout.addWidget(self._mode_value_text, 4, 1, 1, 1,
                         Qt.AlignVCenter)

        layout.addWidget(self._auto_return_button, 5, 0, 1, 2,
                         Qt.AlignVCenter)
        layout.addWidget(start_button, 6, 0, 1, 2,
                         Qt.AlignVCenter)
        layout.addWidget(help_button, 7, 0, 1, 2,
                         Qt.AlignVCenter)

        self.set_auto_return.emit(self._auto_return)

        widget = QWidget()
        widget.setLayout(layout)

        self.addWidget(widget)

    @QtCore.pyqtSlot(int, int, int, int, str)
    def update_control_values(self, pitch=0, roll=0, yaw=0, altitude=0,
                              mode="Unkwnown"):

        self._pitch_value_text.setText(str(pitch))
        self._roll_value_text.setText(str(roll))
        self._yaw_value_text.setText(str(yaw))
        self._altitude_value_text.setText(str(altitude + 100))
        self._mode_value_text.setText(mode)

    @QtCore.pyqtSlot()
    def _set_auto_return(self):
        if self._auto_return:
            self._auto_return_button.setDown(False)
            self._auto_return = False
        else:
            self._auto_return_button.setDown(True)
            self._auto_return = True

        self.set_auto_return.emit(self._auto_return)

    @QtCore.pyqtSlot()
    def _show_rc_help(self):

        help_text = "W: +Pitch\n" \
                    "S: -Pitch\n" \
                    "A: +Roll\n" \
                    "D: -Roll\n" \
                    "Q: +Yaw\n" \
                    "E: -Yaw\n" \
                    "R: +Altitude\n" \
                    "F: -Altitude\n" \
                    "C: Clear values\n" \
                    "L: Land\n" \
                    "K: Kill motors\n" \
                    "1: Flight mode FAIL_SAFE\n" \
                    "2: Flight mode MANUAL\n" \
                    "3: Flight mode KEEP ALTITUDE\n"

        QMessageBox.information(self, "RC controls", help_text)


def _create_text(text, alignment):
    text_label = QLabel()
    text_label.setAlignment(alignment)
    text_label.setText(text)
    return text_label
