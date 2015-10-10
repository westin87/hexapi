#!/usr/bin/env python3

import sys
import logging
from PyQt5.QtCore import pyqtSignal
import pkg_resources

from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import QtCore

from hexacommon.common.gps_data import GPSData

from hexagui.network.network_handler import NetworkHandler
from hexagui.toolbars.logging_toolbar import LoggingToolbar
from hexagui.toolbars.mode_selection_toolbar import ModeSelectionToolbar
from hexagui.toolbars.rc_toolbar import RemoteControlToolbar
from hexagui.toolbars.regulator_toolbar import RegulatorToolbar
from hexagui.toolbars.network_toolbar import NetworkToolbar
from hexagui.widgets.map_label import MapLabel
from hexagui.utils import recorders


class HexapiGUI(QMainWindow):
    update_control_values = pyqtSignal(int, int, int, int, str)

    def __init__(self):
        super(HexapiGUI, self).__init__()
        self.setWindowTitle("Hexacopter controller")

        self._set_application_style()

        # Parameter initialization:
        self._altitude = -100
        self._pitch = 0
        self._yaw = 0
        self._roll = 0
        self._copter_mode = "ATTI"
        self._latest_hexapi_point = (58.376801, 15.647814)

        self._auto_return = False
        self._pressed_keys = []

        self._add_map()

        self._start_keyboard_timer()

        self._nh = NetworkHandler()

        self._register_network_callbacks()
        self._nh.start()

        self._add_network_toolbar()

        #self._add_mode_selection_toolbar()

        self._add_rc_toolbar()

        self._add_regulator_setting_toolbar()

        self._add_logging_toolbar()

    # Initialization functions
    def _add_map(self):
        self._map = MapLabel(parent=self, center=self._latest_hexapi_point)
        self.setCentralWidget(self._map)
        self._map.setFocus()

    def _start_keyboard_timer(self):
        key_timer = QtCore.QTimer(self)
        key_timer.timeout.connect(self._handel_key_presses)
        key_timer.start(30)

    def _register_network_callbacks(self):
        self._nh.register_callback(self._receive_gps_data, "GPS_DATA")
        self._nh.register_callback(recorders.receive_acc_data, "ACC_DATA")
        self._nh.register_callback(recorders.receive_mag_data, "MAG_DATA")
        self._nh.register_callback(recorders.receive_ang_data, "ANG_DATA")

    def _add_logging_toolbar(self):
        logging_toolbar = LoggingToolbar(self._nh)
        self.addToolBar(QtCore.Qt.RightToolBarArea, logging_toolbar)

    def _add_regulator_setting_toolbar(self):
        regulator_toolbar = RegulatorToolbar(self._nh)
        self.addToolBar(QtCore.Qt.RightToolBarArea, regulator_toolbar)

    def _add_rc_toolbar(self):
        rc_toolbar = RemoteControlToolbar()
        rc_toolbar.start_motors.connect(self._start_motors)
        rc_toolbar.set_auto_return.connect(self._set_auto_return)
        self.update_control_values.connect(rc_toolbar.update_control_values)

        self.addToolBar(QtCore.Qt.RightToolBarArea, rc_toolbar)

    def _add_mode_selection_toolbar(self):
        mode_toolbar = ModeSelectionToolbar(self._nh)
        #mode_toolbar.switch_mode.connect()
        self.addToolBar(QtCore.Qt.TopToolBarArea, mode_toolbar)

    def _add_network_toolbar(self):
        network_toolbar = NetworkToolbar(self._nh)
        network_toolbar.reset_hexacopter_parameters.connect(
            self._reset_controls)
        self.addToolBar(QtCore.Qt.TopToolBarArea, network_toolbar)

    def _set_application_style(self):
        self.setMinimumSize(1024, 640)

        style_file_path = pkg_resources.resource_filename(__name__,
                                                          'resources/app_style.qss')
        with open(style_file_path, 'r') as style_file_object:
            self.setStyleSheet(style_file_object.read())

    # Qt event handling functions
    def closeEvent(self, event):
        self._nh.stop()
        super(HexapiGUI, self).closeEvent(event)

    def keyPressEvent(self, event):
        self._pressed_keys.append(event.key())

    def keyReleaseEvent(self, event):
        if event.key() in self._pressed_keys:
            self._pressed_keys.remove(event.key())

    # Other
    def _update_control_values(self):
        self.update_control_values.emit(
            self._pitch, self._roll, self._yaw, self._altitude,
            self._copter_mode)

    def _receive_gps_data(self, raw_gps_data):
        gps_data = GPSData(data_str=raw_gps_data)
        self._latest_hexapi_point = (gps_data.data['latitude'],
                                     gps_data.data['longitude'])

        self._map.add_point(self._latest_hexapi_point)

    # Slots
    @QtCore.pyqtSlot()
    def _reset_controls(self):
        self._altitude = -100
        self._pitch = 0
        self._yaw = 0
        self._roll = 0
        self._copter_mode = "ATTI"

        self._update_control_values()

    @QtCore.pyqtSlot()
    def _start_motors(self):
        self._nh.send_command("START_MOTORS")
        self._reset_controls()
        self._altitude = -75

        self._update_control_values()

    @QtCore.pyqtSlot(bool)
    def _set_auto_return(self, auto_return):
        self._auto_return = auto_return

    @QtCore.pyqtSlot()
    def _handel_key_presses(self):
        if self._auto_return:
            if _opposite_sign(self._pitch) or \
                    _opposite_sign(self._roll) or \
                    _opposite_sign(self._yaw):
                self._pitch += _opposite_sign(self._pitch)
                self._roll += _opposite_sign(self._roll)
                self._yaw += _opposite_sign(self._yaw)
                self._nh.send_command("SET_PITCH", self._pitch)
                self._nh.send_command("SET_ROLL", self._roll)
                self._nh.send_command("SET_YAW", self._yaw)

                self._update_control_values()

        for key in self._pressed_keys:
            if key == QtCore.Qt.Key_W:
                if _in_rang(self._pitch + 2):
                    self._pitch += 2
                    self._nh.send_command("SET_PITCH", self._pitch)
            if key == QtCore.Qt.Key_S:
                if _in_rang(self._pitch - 2):
                    self._pitch -= 2
                    self._nh.send_command("SET_PITCH", self._pitch)
            if key == QtCore.Qt.Key_A:
                if _in_rang(self._roll - 2):
                    self._roll -= 2
                    self._nh.send_command("SET_ROLL", self._roll)
            if key == QtCore.Qt.Key_D:
                if _in_rang(self._roll + 2):
                    self._roll += 2
                    self._nh.send_command("SET_ROLL", self._roll)
            if key == QtCore.Qt.Key_Q:
                if _in_rang(self._yaw - 2):
                    self._yaw -= 2
                    self._nh.send_command("SET_YAW", self._yaw)
            if key == QtCore.Qt.Key_E:
                if _in_rang(self._yaw + 2):
                    self._yaw += 2
                    self._nh.send_command("SET_YAW", self._yaw)
            if key == QtCore.Qt.Key_R:
                if _in_rang(self._altitude + 1):
                    self._altitude += 1
                    self._nh.send_command("SET_ALTITUDE", self._altitude)
            if key == QtCore.Qt.Key_F:
                if _in_rang(self._altitude - 1):
                    self._altitude -= 1
                    self._nh.send_command("SET_ALTITUDE", self._altitude)
            if key == QtCore.Qt.Key_1:
                self._copter_mode = "FS"
                self._nh.send_command("SET_MODE", self._copter_mode)
            if key == QtCore.Qt.Key_2:
                self._copter_mode = "MAN"
                self._nh.send_command("SET_MODE", self._copter_mode)
            if key == QtCore.Qt.Key_3:
                self._copter_mode = "ATTI"
                self._nh.send_command("SET_MODE", self._copter_mode)
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


# Mixes utility functions
def _in_rang(value):
    return -100 <= value <= 100


def _opposite_sign(x):
    if x > 0:
        ans = -1
    elif x < 0:
        ans = 1
    else:
        ans = 0
    return ans


def main():
    logging.basicConfig(filename='hexapi_gui.log', level=logging.DEBUG)
    app = QApplication([])
    win = HexapiGUI()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
