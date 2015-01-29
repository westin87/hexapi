#!/usr/bin/env python3

import sys
import logging

from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton,\
    QGridLayout, QScrollArea, QLineEdit, QComboBox, QTabWidget,\
    QHBoxLayout
from PyQt5 import QtCore

from network.network_handler import NetworkHandler
from widgets.map_label import MapLabel
from common.gps_data import GPSData


class HexapiGUI(QWidget):
    def __init__(self):
        super(HexapiGUI, self).__init__()
        self.setWindowTitle("Hexacopter controller")
        self.setGeometry(0, 0, 1024, 640)

        with open("app_style.qss", 'r') as style_file:
            app.setStyleSheet(style_file.read())

        self.__altitude = -100
        self.__pitch = 0
        self.__yaw = 0
        self.__roll = 0
        self.__mode_switch = "ATTI"
        self.__latest_hexapi_point = (58.376801, 15.647814)

        map_area = QScrollArea()
        map_area.setMinimumSize(480, 480)
        map_area.setMaximumSize(640, 640)
        self.__map_label = MapLabel(parent=None, center=self.__latest_hexapi_point)
        map_area.setWidget(self.__map_label)

        main_layout = QHBoxLayout()
        control_layout = QGridLayout()

        main_layout.addWidget(map_area)
        main_layout.addLayout(control_layout)

        self.__add_network_control(control_layout)
        self.__add_mode_selection(control_layout)
        self.__add_control_display(control_layout)
        self.setLayout(main_layout)

        key_timer = QtCore.QTimer(self)
        key_timer.timeout.connect(self.__handel_key_presses)
        key_timer.start(30)

        ping_timer = QtCore.QTimer(self)
        ping_timer.timeout.connect(self.__send_ping)
        ping_timer.start(500)

        self.__connected = False
        self.__auto_return = False
        self.__pressed_keys = []
        self.__nh = NetworkHandler()
        self.__nh.register_callback(self.__receive_gps_data, "GPS_DATA")
        self.__nh.register_callback(self.__receive_acc_data, "ACC_DATA")
        self.__nh.register_callback(self.__receive_mag_data, "MAG_DATA")
        self.__nh.start()

    def closeEvent(self, event):
        self.__nh.stop()
        super(HexapiGUI, self).closeEvent(event)

    def keyPressEvent(self, event):
        self.__pressed_keys.append(event.key())

    def keyReleaseEvent(self, event):
        if event.key() in self.__pressed_keys:
            self.__pressed_keys.remove(event.key())

    def __receive_gps_data(self, raw_gps_data):
        gps_data = GPSData(data_str=raw_gps_data)
        self.__latest_hexapi_point = (gps_data.data['latitude'],
                                      gps_data.data['longitude'])

        self.__map_label.add_point(self.__latest_hexapi_point)

    def __receive_mag_data(self, raw_mag_data):
        mag_data = eval(raw_mag_data)
        print(mag_data)

    def __receive_acc_data(self, raw_acc_data):
        acc_data = eval(raw_acc_data)
        print(acc_data)

    def __reset_controls(self):
        self.__altitude = -100
        self.__pitch = 0
        self.__yaw = 0
        self.__roll = 0
        self.__mode_switch = "ATTI"
        self.__update_control_values()

    def __send_ping(self):
        if self.__connected:
            self.__nh.send_command("PING")

    def __connect(self):
        logging.info("MA: Setting host")
        self.__connected = True
        host_and_port = self.__host_edit.text().split(":")

        if len(host_and_port) == 2:
            port = int(host_and_port[1])
        else:
            port = 4092
        self.__nh.set_host(host_and_port[0], port)

        self.__nh.send_command("SET_PITCH", self.__pitch)
        self.__nh.send_command("SET_ROLL", self.__roll)
        self.__nh.send_command("SET_YAW", self.__yaw)
        self.__nh.send_command("SET_ALTITUDE", self.__altitude)
        self.__nh.send_command("SET_MODE", self.__mode_switch)
        self.__update_control_values()

    def __start_motors(self):
        self.__nh.send_command("START_MOTORS")
        self.__reset_controls()
        self.__altitude = -75
        self.__update_control_values()

    def __land(self):
        self.__nh.send_command("LAND")
        self.__reset_controls()

    def __kill(self):
        self.__nh.send_command("KILL")
        self.__reset_controls()

    def __op_sign(self, x):
        if x > 0:
            ans = -1
        elif x < 0:
            ans = 1
        else:
            ans = 0
        return ans

    def __in_rang(self, value):
        return value >= -100 and value <= 100

    def __set_auto_return(self):
        if self.__auto_return:
            self.__auto_return_button.setDown(False)
            self.__auto_return = False
        else:
            self.__auto_return_button.setDown(True)
            self.__auto_return = True

    def __handel_key_presses(self):
        if self.__auto_return:
            if self.__op_sign(self.__pitch) or\
               self.__op_sign(self.__roll) or\
               self.__op_sign(self.__yaw):
                self.__pitch = self.__pitch + self.__op_sign(self.__pitch)
                self.__roll = self.__roll + self.__op_sign(self.__roll)
                self.__yaw = self.__yaw + self.__op_sign(self.__yaw)
                self.__nh.send_command("SET_PITCH", self.__pitch)
                self.__nh.send_command("SET_ROLL", self.__roll)
                self.__nh.send_command("SET_YAW", self.__yaw)
                self.__update_control_values()

        for key in self.__pressed_keys:
            if key == QtCore.Qt.Key_W:
                if self.__in_rang(self.__pitch + 2):
                    self.__pitch += 2
                    self.__nh.send_command("SET_PITCH", self.__pitch)
            if key == QtCore.Qt.Key_S:
                if self.__in_rang(self.__pitch - 2):
                    self.__pitch -= 2
                    self.__nh.send_command("SET_PITCH", self.__pitch)
            if key == QtCore.Qt.Key_A:
                if self.__in_rang(self.__roll - 2):
                    self.__roll -= 2
                    self.__nh.send_command("SET_ROLL", self.__roll)
            if key == QtCore.Qt.Key_D:
                if self.__in_rang(self.__roll + 2):
                    self.__roll += 2
                    self.__nh.send_command("SET_ROLL", self.__roll)
            if key == QtCore.Qt.Key_Q:
                if self.__in_rang(self.__yaw - 2):
                    self.__yaw -= 2
                    self.__nh.send_command("SET_YAW", self.__yaw)
            if key == QtCore.Qt.Key_E:
                if self.__in_rang(self.__yaw + 2):
                    self.__yaw += 2
                    self.__nh.send_command("SET_YAW", self.__yaw)
            if key == QtCore.Qt.Key_R:
                if self.__in_rang(self.__altitude + 1):
                    self.__altitude += 1
                    self.__nh.send_command("SET_ALTITUDE", self.__altitude)
            if key == QtCore.Qt.Key_F:
                if self.__in_rang(self.__altitude - 1):
                    self.__altitude -= 1
                    self.__nh.send_command("SET_ALTITUDE", self.__altitude)
            if key == QtCore.Qt.Key_1:
                self.__mode_switch = "FS"
                self.__nh.send_command("SET_MODE", self.__mode_switch)
            if key == QtCore.Qt.Key_2:
                self.__mode_switch = "MAN"
                self.__nh.send_command("SET_MODE", self.__mode_switch)
            if key == QtCore.Qt.Key_3:
                self.__mode_switch = "ATTI"
                self.__nh.send_command("SET_MODE", self.__mode_switch)
            if key == QtCore.Qt.Key_C:
                self.__pitch = 0
                self.__roll = 0
                self.__yaw = 0
                self.__nh.send_command("SET_PITCH", self.__pitch)
                self.__nh.send_command("SET_ROLL", self.__roll)
                self.__nh.send_command("SET_YAW", self.__yaw)
            if key == QtCore.Qt.Key_L:
                self.__land()
            if key == QtCore.Qt.Key_O:
                self.__start_motors()
            if key == QtCore.Qt.Key_K:
                self.__kill()

            self.__update_control_values()

    def __add_network_control(self, layout):
        host_text = QLabel()
        host_text.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignCenter)
        host_text.setText("Connect to hexapi:")

        self.__host_edit = QLineEdit()
        self.__host_edit.setMinimumWidth(100)
        self.__host_edit.setAlignment(QtCore.Qt.AlignRight)
        self.__host_edit.setPlaceholderText("192.169.1.2")
        connect_button = QPushButton("Set host")
        connect_button.clicked.connect(self.__connect)

        land_button = QPushButton("Land")
        land_button.clicked.connect(self.__land)

        kill_button = QPushButton("Kill!")
        kill_button.clicked.connect(self.__kill)

        layout.addWidget(host_text, 0, 0, 1, 1)
        layout.addWidget(self.__host_edit, 0, 2, 1, 3)
        layout.addWidget(connect_button, 0, 5, 1, 1)
        layout.addWidget(land_button, 2, 0, 1, 6)
        layout.addWidget(kill_button, 3, 0, 1, 6)

    def __switch_control_mode(self):
        command = ""
        if self.__mode_selection.currentText() == "RC":
            command = "START_PROG_RC"
        elif self.__mode_selection.currentText() == "GPS":
            command = "START_PROG_GPS"
        else:
            command = "START_PROG_RC"

        self.__nh.send_command(command)

    def __add_mode_selection(self, layout):
        mode_text = QLabel()
        mode_text.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignCenter)
        mode_text.setText("Select mode:")
        self.__mode_selection = QComboBox()
        self.__mode_selection.addItem("RC")
        self.__mode_selection.addItem("GPS")
        select_button = QPushButton("Select")
        select_button.clicked.connect(self.__switch_control_mode)
        layout.addWidget(mode_text, 1, 0, 1, 1)
        layout.addWidget(self.__mode_selection, 1, 3, 1, 2)
        layout.addWidget(select_button, 1, 5, 1, 1)

    def __add_control_display(self, layout):
        tabs = QTabWidget()
        rc_layout = QGridLayout()
        gps_layout = QGridLayout()

        self.__add_rc_control_display(rc_layout)
        self.__add_gps_control_display(gps_layout)

        rc_widget = QWidget()
        gps_widget = QWidget()

        rc_widget.setLayout(rc_layout)
        gps_widget.setLayout(gps_layout)
        tabs.addTab(rc_widget, "RC")
        tabs.addTab(gps_widget, "GPS")
        layout.addWidget(tabs, 4, 0, 1, 6)

    def __add_rc_control_display(self, layout):

        pitch_static_text = self.__create_text("Pitch:", QtCore.Qt.AlignLeft)
        self.__pitch_value_text = self.__create_text("0", QtCore.Qt.AlignRight)

        roll_static_text = self.__create_text("Roll:", QtCore.Qt.AlignLeft)
        self.__roll_value_text = self.__create_text("0", QtCore.Qt.AlignRight)

        yaw_static_text = self.__create_text("Yaw:", QtCore.Qt.AlignLeft)
        self.__yaw_value_text = self.__create_text("0", QtCore.Qt.AlignRight)

        altitude_static_text = self.__create_text("Altitude:",
                                                  QtCore.Qt.AlignLeft)
        self.__altitude_value_text = self.__create_text("0",
                                                        QtCore.Qt.AlignRight)

        mode_static_text = self.__create_text("Mode:", QtCore.Qt.AlignLeft)
        self.__mode_value_text = self.__create_text("0", QtCore.Qt.AlignRight)

        key_map = "W: +Pitch\n"\
            "S: -Pitch\n"\
            "A: +Roll\n"\
            "D: -Roll\n"\
            "Q: +Yaw\n"\
            "E: -Yaw\n"\
            "R: +Altitude\n"\
            "F: -Altitude\n"\
            "C: Clear values\n"\
            "L: Land\n"\
            "K: Kill motors\n"\
            "1: Flight mode FAIL_SAFE\n"\
            "2: Flight mode MANUAL\n"\
            "3: Flight mode KEEP ALTITUDE\n"

        keys_text = self.__create_text(key_map, QtCore.Qt.AlignLeft)

        self.__update_control_values()

        auto_return_button = QPushButton("Auto return")
        auto_return_button.clicked.connect(self.__set_auto_return)

        start_button = QPushButton("Start motors")
        start_button.clicked.connect(self.__start_motors)

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

        layout.addWidget(auto_return_button, 0, 3, 1, 2,
                         QtCore.Qt.AlignVCenter)

        layout.addWidget(start_button, 1, 3, 1, 2,
                         QtCore.Qt.AlignVCenter)
        layout.addWidget(keys_text, 5, 0, 4, 2,
                         QtCore.Qt.AlignVCenter)

        for i in range(5):
            layout.setRowMinimumHeight(i, 26)

        layout.setRowStretch(6, 1)

    def __add_gps_control_display(self, layout):
        draw_route_button = QPushButton("Draw route")
        draw_route_button.clicked.connect(self.__map_label.enable_drawing)
        layout.addWidget(draw_route_button, 0, 0, 1, 1, QtCore.Qt.AlignVCenter)

        set_route_button = QPushButton("Set route")
        set_route_button.clicked.connect(self.__map_label.disable_drawing)
        path = self.__map_label.get_drawn_path()
        # Send path
        layout.addWidget(set_route_button, 0, 1, 1, 1, QtCore.Qt.AlignVCenter)

        clear_route_button = QPushButton("Clear route")
        clear_route_button.clicked.connect(self.__map_label.clear_drawn_path)
        layout.addWidget(clear_route_button, 0, 2, 1, 1, QtCore.Qt.AlignVCenter)

        center_button = QPushButton("Center map")
        center_button.clicked.connect(lambda: self.__map_label.set_center(
            self.__latest_hexapi_point))
        layout.addWidget(center_button, 1, 0, 1, 1, QtCore.Qt.AlignVCenter)

        show_path_button = QPushButton("Show path")
        show_path_button.clicked.connect(self.__map_label.show_input_path)
        layout.addWidget(show_path_button, 2, 0, 1, 1, QtCore.Qt.AlignVCenter)

        start_button = QPushButton("Start motors")
        start_button.clicked.connect(self.__start_motors)
        layout.addWidget(start_button, 1, 1, 1, 1, QtCore.Qt.AlignVCenter)

        start_route_button = QPushButton("Fly route")
        start_route_button.clicked.connect(self.__map_label.clear_drawn_path)
        # Send start command
        layout.addWidget(start_route_button, 1, 2, 1, 1, QtCore.Qt.AlignVCenter)

        layout.setRowStretch(20, 1)

    def __create_text(self, text, alignment):
        text_label = QLabel()
        text_label.setAlignment(alignment)
        text_label.setText(text)
        return text_label

    def __update_control_values(self):
        self.__pitch_value_text.setText(str(self.__pitch))
        self.__roll_value_text.setText(str(self.__roll))
        self.__yaw_value_text.setText(str(self.__yaw))
        self.__altitude_value_text.setText(str(self.__altitude+100))
        self.__mode_value_text.setText(self.__mode_switch)


if __name__ == "__main__":
    logging.basicConfig(filename='hexapi_gui.log', level=logging.DEBUG)
    app = QApplication([])
    win = HexapiGUI()
    win.show()
    sys.exit(app.exec_())
