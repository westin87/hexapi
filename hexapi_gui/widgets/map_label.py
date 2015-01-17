#!/usr/bin/env python3

from PyQt5.QtWidgets import QLabel, QPushButton
from PyQt5 import QtGui, QtCore
from utils import gmaps


class MapLabel(QLabel):
    def __init__(self, parent=None, center=(0, 0), zoom=17):
        super(MapLabel, self).__init__(parent)
        self.__drawing_possible = False
        self.__show_input_path = True
        self.__drawn_path_map_coordinates = []
        self.__drawn_path = []
        self.__input_path_map_coordinates = []
        self.__input_path = []
        self.__center = center
        self.__zoom = zoom
        self.setPixmap(gmaps.get_map(self.__center, self.__zoom))
        self.__mouse_press_pos = None
        self.__dy_offset = 0
        self.__dx_offset = 0
        self.__count = 0

    def __set_map(self):
        self.__update_drawing_paths()
        self.setPixmap(gmaps.get_map(self.__center, self.__zoom))
        self.update()

    def add_point(self, point):
        self.__input_path_map_coordinates.append(point)
        self.__update_drawing_paths()
        self.update()

    def clear_input_path(self):
        self.__input_path_map_coordinates = []
        self.__update_drawing_paths()
        self.update()

    def clear_drawn_path(self):
        self.__drawn_path_map_coordinates = []
        self.__update_drawing_paths()
        self.update()

    def get_drawn_path(self):
        return self.__drawn_path_map_coordinates

    def enable_drawing(self):
        self.__drawing_possible = True

    def disable_drawing(self):
        self.__drawing_possible = False

    def show_input_path(self):
        if self.__show_input_path:
            self.__show_input_path = False
        else:
            self.__show_input_path = True
        self.update()

    def set_center(self, point):
        self.__center = point
        self.__set_map()

    def wheelEvent(self, event):
        self.__count += 1
        if self.__count % 1 == 0:
            # TODO: Change to sign of angle delta.
            self.__zoom += int(event.angleDelta().y()/120)
            if self.__zoom > 22:
                self.__zoom = 22
            elif self.__zoom < 1:
                self.__zoom = 1
            else:
                self.__set_map()

    def mousePressEvent(self, event):
        self.__mouse_press_pos = event.pos()

    def mouseMoveEvent(self, event):
        self.__dy_offset = event.y() - self.__mouse_press_pos.y()
        self.__dx_offset = event.x() - self.__mouse_press_pos.x()
        self.update()

    def mouseReleaseEvent(self, event):
        if (self.__drawing_possible and
                (abs(event.x()-self.__mouse_press_pos.x()) < 4) and
                (abs(event.y()-self.__mouse_press_pos.y()) < 4)):

            cy = event.y()-gmaps.DEF_MAPS_SIZE/2
            cx = event.x()-gmaps.DEF_MAPS_SIZE/2

            map_pos = (self.__center[0]+gmaps.pix_to_deg_lat(cy,
                                                             self.__zoom,
                                                             self.__center[0]),
                       self.__center[1]+gmaps.pix_to_deg_long(cx,
                                                              self.__zoom))

            self.__drawn_path_map_coordinates.append(map_pos)
            self.__update_drawing_paths()
            self.update()
        else:
            dy = self.__mouse_press_pos.y() - event.y()
            dx = self.__mouse_press_pos.x() - event.x()

            map_pos = (self.__center[0]+gmaps.pix_to_deg_lat(dy,
                                                             self.__zoom,
                                                             self.__center[0]),
                       self.__center[1]+gmaps.pix_to_deg_long(dx,
                                                              self.__zoom))

            self.__center = map_pos
            self.__set_map()

        self.__dy_offset = 0
        self.__dx_offset = 0

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        size = self.parent().size()
        self.setGeometry(0, 0, size.width(), size.height())

        painter.setBrush(QtGui.QColor(20, 40, 60))
        painter.drawRect(0, 0, size.width(), size.height())
        painter.drawPixmap(self.__dx_offset, self.__dy_offset, self.pixmap())

        painter.setBrush(QtGui.QBrush())

        self.__draw_path(painter, self.__drawn_path, QtCore.Qt.blue)
        if self.__drawn_path:
            self.__draw_point(painter, self.__drawn_path[-1],
                              QtCore.Qt.darkBlue)

        if self.__show_input_path:
            self.__draw_path(painter, self.__input_path, QtCore.Qt.magenta)
        if self.__input_path:
            self.__draw_point(painter, self.__input_path[-1],
                              QtCore.Qt.darkMagenta)

    def __draw_point(self, painter, point, color):
        radius = 6

        painter.setPen(QtGui.QPen())
        painter.setBrush(color)

        painter.drawEllipse(point[0]-radius+self.__dx_offset,
                            point[1]-radius+self.__dy_offset,
                            2*radius, 2*radius)

        painter.setBrush(QtGui.QBrush())

    def __draw_path(self, painter, path, color):
        draw_path = QtGui.QPainterPath()

        for i, (x, y) in enumerate(path):
            if i == 0:
                draw_path.moveTo(x+self.__dx_offset, y+self.__dy_offset)
            else:
                draw_path.lineTo(x+self.__dx_offset, y+self.__dy_offset)

        painter.setPen(QtGui.QPen(color, 3, QtCore.Qt.SolidLine))
        painter.drawPath(draw_path)

    def __update_drawing_paths(self):
        self.__drawn_path = []
        self.__input_path = []
        for i, coord in enumerate(self.__drawn_path_map_coordinates):
            y = (gmaps.deg_lat_to_pix(coord[0] - self.__center[0], self.__zoom,
                                      self.__center[0]) +
                 gmaps.DEF_MAPS_SIZE / 2)

            x = (gmaps.deg_long_to_pix(coord[1] - self.__center[1], self.__zoom) +
                 gmaps.DEF_MAPS_SIZE / 2)

            self.__drawn_path.append((x, y))

        for i, coord in enumerate(self.__input_path_map_coordinates):
            y = (gmaps.deg_lat_to_pix(coord[0] - self.__center[0], self.__zoom,
                                      self.__center[0]) +
                 gmaps.DEF_MAPS_SIZE / 2)

            x = (gmaps.deg_long_to_pix(coord[1] - self.__center[1], self.__zoom) +
                 gmaps.DEF_MAPS_SIZE / 2)

            self.__input_path.append((x, y))