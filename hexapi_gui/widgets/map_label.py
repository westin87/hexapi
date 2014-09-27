#!/usr/bin/env python3

from PyQt5.QtWidgets import QLabel
from PyQt5 import QtGui
from utils.gmaps import get_map, pix_to_deg_lat, pix_to_deg_long,\
    DEF_MAPS_SIZE


class MapLabel(QLabel):
    def __init__(self, parent=None, center=(0, 0), zoom=17):
        super(MapLabel, self).__init__(parent)
        self.__path = []
        self.__center = center
        self.__zoom = zoom
        self.setPixmap(get_map(self.__center, self.__zoom))
        self.__mouse_press_pos = None
        self.__last_mouse_pos = None
        self.__count = 0

    def __set_map(self, center, zoom, path):
        # TODO: Some smart stuff to buffer map images.
        self.setPixmap(get_map(center, zoom, path=path))

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
                self.__set_map(self.__center, self.__zoom, self.__path)

    def mousePressEvent(self, event):
        self.__mouse_press_pos = event.pos()
        self.__last_mouse_pos = event.pos()

    def mouseMoveEvent(self, event):
        dy = self.__last_mouse_pos.y() - event.y()
        dx = self.__last_mouse_pos.x() - event.x()

        map_pos = (self.__center[0]+pix_to_deg_lat(dy,
                                                   self.__zoom,
                                                   self.__center[0]),
                   self.__center[1]+pix_to_deg_long(dx,
                                                    self.__zoom))

        self.__center = map_pos
        self.__set_map(self.__center, self.__zoom, self.__path)
        self.__last_mouse_pos = event.pos()

    def mouseReleaseEvent(self, event):
        if (abs(event.x()-self.__mouse_press_pos.x()) < 1) and\
           (abs(event.y()-self.__mouse_press_pos.y()) < 1):
            cy = event.y()-DEF_MAPS_SIZE/2
            cx = event.x()-DEF_MAPS_SIZE/2

            map_pos = (self.__center[0]+pix_to_deg_lat(cy,
                                                       self.__zoom,
                                                       self.__center[0]),
                       self.__center[1]+pix_to_deg_long(cx,
                                                        self.__zoom))

            self.__path.append(map_pos)
            self.__set_map(self.__center, self.__zoom, self.__path)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        size = self.parent().size()
        self.setGeometry(0, 0, size.width(), size.height())
        painter.drawPixmap(0, 0, self.pixmap())
