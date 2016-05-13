from PyQt5.QtWidgets import QToolBar


class GpsControlToolbar(QToolBar):
    def __init__(self, network_handler, map):
        super().__init__("GPS Control")

        self._nh = network_handler
        self._map = map

        self._map.enable_drawing = True
        self._map.single_point_mode = True

        self.addAction("Start regulator", self._start_regulator)
        self.addAction("Stop regulator", self._stop_regulator)
        self.addAction("Set target position", self._set_target_posistion)

    def _start_regulator(self):
        self._nh.send_command("START_REGULATOR")

    def _stop_regulator(self):
        self._nh.send_command("STOP_REGULATOR")

    def _set_target_posistion(self):
        path = self._map.get_drawn_path()
        if path:
            latitude, longitude = path[0]
        else:
            latitude, longitude = 0, 0

        self._nh.send_command("SET_TARGET_POSITION", latitude, longitude)

# TODO: Lika som i rc_toolbar
# def _add_gps_control_display(self, layout):
#     draw_route_button = QPushButton("Draw route")
#     draw_route_button.clicked.connect(self._map.enable_drawing)
#     layout.addWidget(draw_route_button, 0, 0, 1, 1, QtCore.Qt.AlignVCenter)
#
#     set_route_button = QPushButton("Set route")
#     set_route_button.clicked.connect(self._map.disable_drawing)
#     path = self._map.get_drawn_path()
#     # Send path
#     layout.addWidget(set_route_button, 0, 1, 1, 1, QtCore.Qt.AlignVCenter)
#
#     clear_route_button = QPushButton("Clear route")
#     clear_route_button.clicked.connect(self._map.clear_drawn_path)
#     layout.addWidget(clear_route_button, 0, 2, 1, 1, QtCore.Qt.AlignVCenter)
#
#     center_button = QPushButton("Center map")
#     center_button.clicked.connect(lambda: self._map.set_center(
#         self._latest_hexapi_point))
#     layout.addWidget(center_button, 1, 0, 1, 1, QtCore.Qt.AlignVCenter)
#
#     show_path_button = QPushButton("Show path")
#     show_path_button.clicked.connect(self._map.show_input_path)
#     layout.addWidget(show_path_button, 2, 0, 1, 1, QtCore.Qt.AlignVCenter)
#
#     start_button = QPushButton("Start motors")
#     start_button.clicked.connect(self._start_motors)
#     layout.addWidget(start_button, 1, 1, 1, 1, QtCore.Qt.AlignVCenter)
#
#     start_route_button = QPushButton("Fly route")
#     start_route_button.clicked.connect(self._map.clear_drawn_path)
#     # Send start command
#     layout.addWidget(start_route_button, 1, 2, 1, 1, QtCore.Qt.AlignVCenter)
#
#     layout.setRowStretch(20, 1)
