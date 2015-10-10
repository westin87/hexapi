#!/usr/bin/env python3

import sys
import logging
import pkg_resources

from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QGridLayout, QMainWindow,
    QToolBar, QMessageBox)
from PyQt5 import QtCore

from hexacommon.common.gps_data import GPSData

from hexagui.network.network_handler import NetworkHandler
from hexagui.toolbars.logging_toolbar import LoggingToolbar
from hexagui.toolbars.mode_selection_toolbar import ModeSelectionToolbar
from hexagui.toolbars.regulator_toolbar import RegulatorToolbar
from hexagui.toolbars.network_toolbar import NetworkToolbar
from hexagui.widgets.map_label import MapLabel
from hexagui.utils import recorders


class HexapiGUI(QMainWindow):
    def __init__(self):
        super(HexapiGUI, self).__init__()
        self.setWindowTitle("Hexacopter controller")
        self.setMinimumSize(1024, 640)

        style_file_path = pkg_resources.resource_filename(__name__,
            'resources/app_style.qss')

        with open(style_file_path, 'r') as style_file_object:
            self.setStyleSheet(style_file_object.read())

        self._altitude = -100
        self._pitch = 0
        self._yaw = 0
        self._roll = 0
        self._mode_switch = "ATTI"
        self._latest_hexapi_point = (58.376801, 15.647814)

        self._map = MapLabel(parent=self, center=self._latest_hexapi_point)

        self.setCentralWidget(self._map)

        self._add_rc_control()

        key_timer = QtCore.QTimer(self)
        key_timer.timeout.connect(self._handel_key_presses)
        key_timer.start(30)

        self._auto_return = False
        self._pressed_keys = []

        self._nh = NetworkHandler()

        self._nh.register_callback(self._receive_gps_data, "GPS_DATA")

        self._nh.register_callback(recorders.receive_acc_data, "ACC_DATA")
        self._nh.register_callback(recorders.receive_mag_data, "MAG_DATA")
        self._nh.register_callback(recorders.receive_ang_data, "ANG_DATA")
        self._nh.start()

        self.addToolBar(QtCore.Qt.RightToolBarArea, RegulatorToolbar(self._nh))

        network_toolbar = NetworkToolbar(self._nh)
        network_toolbar.reset_hexacopter_parameters.connect(
            self._reset_controls)
        self.addToolBar(QtCore.Qt.TopToolBarArea, network_toolbar)

        mode_toolbar = ModeSelectionToolbar(self._nh)
        mode_toolbar.switch_mode.connect(self._mode_switch)
        self.addToolBar(QtCore.Qt.TopToolBarArea, mode_toolbar)

        logging_toolbar = LoggingToolbar(self._nh)
        self.addToolBar(QtCore.Qt.RightToolBarArea, logging_toolbar)

    def closeEvent(self, event):
        self._nh.stop()
        super(HexapiGUI, self).closeEvent(event)

    def keyPressEvent(self, event):
        self._pressed_keys.append(event.key())

    def keyReleaseEvent(self, event):
        if event.key() in self._pressed_keys:
            self._pressed_keys.remove(event.key())

    def _receive_gps_data(self, raw_gps_data):
        gps_data = GPSData(data_str=raw_gps_data)
        self._latest_hexapi_point = (gps_data.data['latitude'],
                                      gps_data.data['longitude'])

        self._map.add_point(self._latest_hexapi_point)

    @QtCore.pyqtSlot()
    def _reset_controls(self):
        self._altitude = -100
        self._pitch = 0
        self._yaw = 0
        self._roll = 0
        self._mode_switch = "ATTI"

        self._update_control_values()

    @QtCore.pyqtSlot()
    def _start_motors(self):
        self._nh.send_command("START_MOTORS")
        self._reset_controls()
        self._altitude = -75
        self._update_control_values()

    def _op_sign(self, x):
        if x > 0:
            ans = -1
        elif x < 0:
            ans = 1
        else:
            ans = 0
        return ans

    def _in_rang(self, value):
        return value >= -100 and value <= 100

    @QtCore.pyqtSlot()
    def _set_auto_return(self):
        if self._auto_return:
            self.__auto_return_button.setDown(False)
            self._auto_return = False
        else:
            self.__auto_return_button.setDown(True)
            self._auto_return = True

    def _handel_key_presses(self):
        if self._auto_return:
            if self._op_sign(self._pitch) or \
                    self._op_sign(self._roll) or \
                    self._op_sign(self._yaw):
                self._pitch = self._pitch + self._op_sign(self._pitch)
                self._roll = self._roll + self._op_sign(self._roll)
                self._yaw = self._yaw + self._op_sign(self._yaw)
                self._nh.send_command("SET_PITCH", self._pitch)
                self._nh.send_command("SET_ROLL", self._roll)
                self._nh.send_command("SET_YAW", self._yaw)
                self._update_control_values()

        for key in self._pressed_keys:
            if key == QtCore.Qt.Key_W:
                if self._in_rang(self._pitch + 2):
                    self._pitch += 2
                    self._nh.send_command("SET_PITCH", self._pitch)
            if key == QtCore.Qt.Key_S:
                if self._in_rang(self._pitch - 2):
                    self._pitch -= 2
                    self._nh.send_command("SET_PITCH", self._pitch)
            if key == QtCore.Qt.Key_A:
                if self._in_rang(self._roll - 2):
                    self._roll -= 2
                    self._nh.send_command("SET_ROLL", self._roll)
            if key == QtCore.Qt.Key_D:
                if self._in_rang(self._roll + 2):
                    self._roll += 2
                    self._nh.send_command("SET_ROLL", self._roll)
            if key == QtCore.Qt.Key_Q:
                if self._in_rang(self._yaw - 2):
                    self._yaw -= 2
                    self._nh.send_command("SET_YAW", self._yaw)
            if key == QtCore.Qt.Key_E:
                if self._in_rang(self._yaw + 2):
                    self._yaw += 2
                    self._nh.send_command("SET_YAW", self._yaw)
            if key == QtCore.Qt.Key_R:
                if self._in_rang(self._altitude + 1):
                    self._altitude += 1
                    self._nh.send_command("SET_ALTITUDE", self._altitude)
            if key == QtCore.Qt.Key_F:
                if self._in_rang(self._altitude - 1):
                    self._altitude -= 1
                    self._nh.send_command("SET_ALTITUDE", self._altitude)
            if key == QtCore.Qt.Key_1:
                self._mode_switch = "FS"
                self._nh.send_command("SET_MODE", self._mode_switch)
            if key == QtCore.Qt.Key_2:
                self._mode_switch = "MAN"
                self._nh.send_command("SET_MODE", self._mode_switch)
            if key == QtCore.Qt.Key_3:
                self._mode_switch = "ATTI"
                self._nh.send_command("SET_MODE", self._mode_switch)
            if key == QtCore.Qt.Key_C:
                self._pitch = 0
                self._roll = 0
                self._yaw = 0
                self._nh.send_command("SET_PITCH", self._pitch)
                self._nh.send_command("SET_ROLL", self._roll)
                self._nh.send_command("SET_YAW", self._yaw)
            if key == QtCore.Qt.Key_L:
                self._land()
            if key == QtCore.Qt.Key_O:
                self._start_motors()
            if key == QtCore.Qt.Key_K:
                self._kill()

            self._update_control_values()

    @QtCore.pyqtSlot()
    def _switch_control_mode(self, mode):
        if mode == "RC":
            command = "START_PROG_RC"
        elif mode == "GPS":
            command = "START_PROG_GPS"
        else:
            command = "START_PROG_RC"

        self._nh.send_command(command)

    def _add_rc_control(self):
        toolbar = QToolBar("Control display")

        rc_layout = QGridLayout()
        self._add_rc_control_display(rc_layout)
        rc_widget = QWidget()
        rc_widget.setLayout(rc_layout)

        toolbar.addWidget(rc_widget)

        self.addToolBar(QtCore.Qt.RightToolBarArea, toolbar)

    def _add_gps_control(self):
        toolbar = QToolBar("Control display")

        gps_layout = QGridLayout()
        self._add_gps_control_display(gps_layout)
        gps_widget = QWidget()
        gps_widget.setLayout(gps_layout)

        toolbar.addWidget(gps_widget)

        self.addToolBar(QtCore.Qt.RightToolBarArea, toolbar)

    def _add_rc_control_display(self, layout):

        pitch_static_text = self._create_text("Pitch:", QtCore.Qt.AlignLeft)
        self.__pitch_value_text = self._create_text("0", QtCore.Qt.AlignRight)

        roll_static_text = self._create_text("Roll:", QtCore.Qt.AlignLeft)
        self.__roll_value_text = self._create_text("0", QtCore.Qt.AlignRight)

        yaw_static_text = self._create_text("Yaw:", QtCore.Qt.AlignLeft)
        self.__yaw_value_text = self._create_text("0", QtCore.Qt.AlignRight)

        altitude_static_text = self._create_text("Altitude:",
                                                  QtCore.Qt.AlignLeft)
        self.__altitude_value_text = self._create_text("0",
                                                        QtCore.Qt.AlignRight)

        mode_static_text = self._create_text("Mode:", QtCore.Qt.AlignLeft)
        self.__mode_value_text = self._create_text("0", QtCore.Qt.AlignRight)

        self._update_control_values()

        auto_return_button = QPushButton("Auto return")
        auto_return_button.clicked.connect(self._set_auto_return)

        start_button = QPushButton("Start motors")
        start_button.clicked.connect(self._start_motors)

        help_button = QPushButton("Show RC help")
        help_button.clicked.connect(self._show_rc_help)

        layout.addWidget(pitch_static_text, 0, 0, 1, 1,
                         QtCore.Qt.AlignVCenter)
        layout.addWidget(self.__pitch_value_text, 0, 1, 1, 1,
                         QtCore.Qt.AlignVCenter)

        layout.addWidget(roll_static_text, 1, 0, 1, 1,
                         QtCore.Qt.AlignVCenter)
        layout.addWidget(self.__roll_value_text, 1, 1, 1, 1,
                         QtCore.Qt.AlignVCenter)

        layout.addWidget(yaw_static_text, 2, 0, 1, 1,
                         QtCore.Qt.AlignVCenter)
        layout.addWidget(self.__yaw_value_text, 2, 1, 1, 1,
                         QtCore.Qt.AlignVCenter)

        layout.addWidget(altitude_static_text, 3, 0, 1, 1,
                         QtCore.Qt.AlignVCenter)
        layout.addWidget(self.__altitude_value_text, 3, 1, 1, 1,
                         QtCore.Qt.AlignVCenter)

        layout.addWidget(mode_static_text, 4, 0, 1, 1,
                         QtCore.Qt.AlignVCenter)
        layout.addWidget(self.__mode_value_text, 4, 1, 1, 1,
                         QtCore.Qt.AlignVCenter)

        layout.addWidget(auto_return_button, 5, 0, 1, 2,
                         QtCore.Qt.AlignVCenter)
        layout.addWidget(start_button, 6, 0, 1, 2,
                         QtCore.Qt.AlignVCenter)
        layout.addWidget(help_button, 7, 0, 1, 2,
                         QtCore.Qt.AlignVCenter)

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

    def _add_gps_control_display(self, layout):
        draw_route_button = QPushButton("Draw route")
        draw_route_button.clicked.connect(self._map.enable_drawing)
        layout.addWidget(draw_route_button, 0, 0, 1, 1, QtCore.Qt.AlignVCenter)

        set_route_button = QPushButton("Set route")
        set_route_button.clicked.connect(self._map.disable_drawing)
        path = self._map.get_drawn_path()
        # Send path
        layout.addWidget(set_route_button, 0, 1, 1, 1, QtCore.Qt.AlignVCenter)

        clear_route_button = QPushButton("Clear route")
        clear_route_button.clicked.connect(self._map.clear_drawn_path)
        layout.addWidget(clear_route_button, 0, 2, 1, 1, QtCore.Qt.AlignVCenter)

        center_button = QPushButton("Center map")
        center_button.clicked.connect(lambda: self._map.set_center(
            self._latest_hexapi_point))
        layout.addWidget(center_button, 1, 0, 1, 1, QtCore.Qt.AlignVCenter)

        show_path_button = QPushButton("Show path")
        show_path_button.clicked.connect(self._map.show_input_path)
        layout.addWidget(show_path_button, 2, 0, 1, 1, QtCore.Qt.AlignVCenter)

        start_button = QPushButton("Start motors")
        start_button.clicked.connect(self._start_motors)
        layout.addWidget(start_button, 1, 1, 1, 1, QtCore.Qt.AlignVCenter)

        start_route_button = QPushButton("Fly route")
        start_route_button.clicked.connect(self._map.clear_drawn_path)
        # Send start command
        layout.addWidget(start_route_button, 1, 2, 1, 1, QtCore.Qt.AlignVCenter)

        layout.setRowStretch(20, 1)

    def _create_text(self, text, alignment):
        text_label = QLabel()
        text_label.setAlignment(alignment)
        text_label.setText(text)
        return text_label

    def _update_control_values(self):
        self.__pitch_value_text.setText(str(self._pitch))
        self.__roll_value_text.setText(str(self._roll))
        self.__yaw_value_text.setText(str(self._yaw))
        self.__altitude_value_text.setText(str(self._altitude + 100))
        self.__mode_value_text.setText(self._mode_switch)


def main():
    logging.basicConfig(filename='hexapi_gui.log', level=logging.DEBUG)
    app = QApplication([])
    win = HexapiGUI()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
