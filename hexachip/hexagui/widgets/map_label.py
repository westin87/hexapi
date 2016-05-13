#!/usr/bin/env python3
from PyQt5.QtCore import Qt

from PyQt5.QtWidgets import QLabel, QPushButton
from PyQt5 import QtGui, QtCore
from hexagui.utils import gmaps


class MapLabel(QLabel):
    def __init__(self, parent=None, center=(0, 0), zoom=17):
        super(MapLabel, self).__init__(parent)

        self.setFocusPolicy(Qt.StrongFocus)

        self.enable_drawing = False
        self.single_point_mode = False
        self._show_input_path = True
        self._drawn_path_map_coordinates = []
        self._drawn_path = []
        self._input_path_map_coordinates = []
        self._input_path = []
        self._center = center
        self._zoom = zoom
        self._mouse_press_pos = None
        self._dy_offset = 0
        self._dx_offset = 0
        self._count = 0

        self.setMinimumSize(480, 480)
        self.setMaximumSize(640, 640)

        self.setPixmap(gmaps.get_map(self._center, self._zoom))

    def _set_map(self):
        self._update_drawing_paths()
        self.setPixmap(gmaps.get_map(self._center, self._zoom))
        self.update()

    def add_point(self, point):
        self._input_path_map_coordinates.append(point)
        self._update_drawing_paths()
        self.update()

    def clear_input_path(self):
        self._input_path_map_coordinates = []
        self._update_drawing_paths()
        self.update()

    def clear_drawn_path(self):
        self._drawn_path_map_coordinates = []
        self._update_drawing_paths()
        self.update()

    def get_drawn_path(self):
        return self._drawn_path_map_coordinates

    def show_input_path(self):
        if self._show_input_path:
            self._show_input_path = False
        else:
            self._show_input_path = True
        self.update()

    def set_center(self, point):
        self._center = point
        self._set_map()

    def wheelEvent(self, event):
        self._count += 1
        if self._count % 1 == 0:
            # TODO: Change to sign of angle delta.
            self._zoom += int(event.angleDelta().y()/120)
            if self._zoom > 22:
                self._zoom = 22
            elif self._zoom < 1:
                self._zoom = 1
            else:
                self._set_map()

    def mousePressEvent(self, event):
        self._mouse_press_pos = event.pos()

    def mouseMoveEvent(self, event):
        self._dy_offset = event.y() - self._mouse_press_pos.y()
        self._dx_offset = event.x() - self._mouse_press_pos.x()
        self.update()

    def mouseReleaseEvent(self, event):
        if (self.enable_drawing and
                (abs(event.x() - self._mouse_press_pos.x()) < 4) and
                (abs(event.y() - self._mouse_press_pos.y()) < 4)):

            cy = event.y() - gmaps.DEF_MAPS_SIZE / 2
            cx = event.x() - gmaps.DEF_MAPS_SIZE / 2

            map_pos = (
                self._center[0] + gmaps.pix_to_deg_lat(cy, self._zoom, self._center[0]),
                self._center[1] + gmaps.pix_to_deg_long(cx, self._zoom))

            if self.single_point_mode:
                self._drawn_path_map_coordinates = [map_pos]
            else:
                self._drawn_path_map_coordinates.append(map_pos)

            self._update_drawing_paths()
            self.update()
        else:
            dy = self._mouse_press_pos.y() - event.y()
            dx = self._mouse_press_pos.x() - event.x()

            map_pos = (
                self._center[0] + gmaps.pix_to_deg_lat(dy, self._zoom, self._center[0]),
                self._center[1] + gmaps.pix_to_deg_long(dx, self._zoom))

            self._center = map_pos
            self._set_map()

        self._dy_offset = 0
        self._dx_offset = 0

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        geometry =  self.geometry()

        painter.setBrush(QtGui.QColor(20, 40, 60))
        painter.setPen(QtGui.QColor(20, 40, 60))
        painter.drawRect(0, 0, geometry.width(), geometry.height())
        painter.drawPixmap(self._dx_offset, self._dy_offset, self.pixmap())

        painter.setBrush(QtGui.QBrush())

        self._draw_path(painter, self._drawn_path, QtCore.Qt.blue)
        if self._drawn_path:
            self._draw_point(painter, self._drawn_path[-1],
                              QtCore.Qt.darkBlue)

        if self._show_input_path:
            self._draw_path(painter, self._input_path, QtCore.Qt.magenta)
        if self._input_path:
            self._draw_point(painter, self._input_path[-1],
                              QtCore.Qt.darkMagenta)

    def _draw_point(self, painter, point, color):
        radius = 6

        painter.setPen(QtGui.QPen())
        painter.setBrush(color)

        painter.drawEllipse(point[0] - radius + self._dx_offset,
                            point[1] - radius + self._dy_offset,
                            2 * radius, 2 * radius)

        painter.setBrush(QtGui.QBrush())

    def _draw_path(self, painter, path, color):
        draw_path = QtGui.QPainterPath()

        for i, (x, y) in enumerate(path):
            if i == 0:
                draw_path.moveTo(x + self._dx_offset, y + self._dy_offset)
            else:
                draw_path.lineTo(x + self._dx_offset, y + self._dy_offset)

        painter.setPen(QtGui.QPen(color, 3, QtCore.Qt.SolidLine))
        painter.drawPath(draw_path)

    def _update_drawing_paths(self):
        self._drawn_path = []
        self._input_path = []
        for i, coord in enumerate(self._drawn_path_map_coordinates):
            y = (gmaps.deg_lat_to_pix(coord[0] - self._center[0], self._zoom,
                                      self._center[0]) +
                 gmaps.DEF_MAPS_SIZE / 2)

            x = (gmaps.deg_long_to_pix(coord[1] - self._center[1], self._zoom) +
                 gmaps.DEF_MAPS_SIZE / 2)

            self._drawn_path.append((x, y))

        for i, coord in enumerate(self._input_path_map_coordinates):
            y = (gmaps.deg_lat_to_pix(coord[0] - self._center[0], self._zoom,
                                      self._center[0]) +
                 gmaps.DEF_MAPS_SIZE / 2)

            x = (gmaps.deg_long_to_pix(coord[1] - self._center[1], self._zoom) +
                 gmaps.DEF_MAPS_SIZE / 2)

            self._input_path.append((x, y))
