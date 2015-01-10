#!/usr/bin/env python3

from PyQt5.QtWidgets import QLabel
from PyQt5 import QtGui, QtCore
from utils.gmaps import get_map, pix_to_deg_lat, pix_to_deg_long,\
    DEF_MAPS_SIZE


class MapLabel(QLabel):
    def __init__(self, parent=None, center=(0, 0), zoom=17):
        super(MapLabel, self).__init__(parent)
        self.__path = []
        self.__path_raw = []
        self.__center = center
        self.__zoom = zoom
        self.setPixmap(get_map(self.__center, self.__zoom))
        self.__mouse_press_pos = None
        self.__dy_offset = 0
        self.__dx_offset = 0
        self.__count = 0

    def __set_map(self):
        # TODO: Some smart stuff to buffer map images.
        self.setPixmap(get_map(self.__center, self.__zoom, path=self.__path))
        self.update()

    def add_point(self, point):
        self.__path.append(point)
        #self.__center = point
        self.__set_map()

    def wheelEvent(self, event):
        self.__count += 1
        if self.__count % 4 == 0:
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
        if (abs(event.x()-self.__mouse_press_pos.x()) < 4) and\
           (abs(event.y()-self.__mouse_press_pos.y()) < 4):
            cy = event.y()-DEF_MAPS_SIZE/2
            cx = event.x()-DEF_MAPS_SIZE/2

            map_pos = (self.__center[0]+pix_to_deg_lat(cy,
                                                       self.__zoom,
                                                       self.__center[0]),
                       self.__center[1]+pix_to_deg_long(cx,
                                                        self.__zoom))

            self.__path.append(map_pos)
            self.__path_raw.append(QtCore.QPoint(event.x(), event.y()))
            self.update()
        else:
            dy = self.__mouse_press_pos.y() - event.y()
            dx = self.__mouse_press_pos.x() - event.x()

            map_pos = (self.__center[0]+pix_to_deg_lat(dy,
                                                       self.__zoom,
                                                       self.__center[0]),
                       self.__center[1]+pix_to_deg_long(dx,
                                                        self.__zoom))

            self.__center = map_pos
            self.__set_map()

        self.__dy_offset = 0
        self.__dx_offset = 0

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        size = self.parent().size()
        self.setGeometry(0, 0, size.width(), size.height())
        painter.drawPixmap(self.__dx_offset, self.__dy_offset, self.pixmap())

        if self.__path_raw:
            self.__draw_path(painter)

    def __draw_path(self, painter):
        pen = QtGui.QPen(QtCore.Qt.red, 2, QtCore.Qt.SolidLine)
        painter.setPen(pen)
        tmp_path = QtGui.QPainterPath()
        tmp_path.moveTo(self.__path_raw[0])
        for coord in self.__path_raw:
            tmp_path.lineTo(coord)
        painter.drawPath(tmp_path)
