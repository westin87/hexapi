import sys

import numpy as np
from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout

from hexacommon.common.coordinates import Vector2D
from hexacoppter.tests.integration.hexacopter_model import HexacopterModel
from hexacoppter.utils.regulator import HexacopterRegulator


class HexacopterSimulator(QWidget):
    TICK_INTERVAL = 25
    TARGET_INTERVAL = 8 * TICK_INTERVAL

    def __init__(self):
        super().__init__()

        start_position = Vector2D(0.5, 0.5)

        self._regulator = HexacopterRegulator()
        self._regulator.set_initial_position(start_position)

        self._hexacopter = HexacopterModel(start_position)
        self._hexacopter.direction = 0
        self._hexacopter.yaw = 0.1
        self._hexacopter.external_force = Vector2D(0, 0.03)

        self._route = iter(
            [Vector2D(0.3, 0.3), Vector2D(0.8, 0.3), Vector2D(0.3, 0.3), Vector2D(0.8, 0.8),
             Vector2D(0.2, 0.7), Vector2D(0.5, 0.3), Vector2D(0.1, 0.2), Vector2D(0.5, 0.5)])

        self._target = Target(Vector2D(0.2, 0.5))

        self._map = Map(self._hexacopter, self._target)

        layout = QVBoxLayout()
        layout.addWidget(self._map)
        self.setLayout(layout)

        self._tick_timer = QTimer()
        self._tick_timer.start(self.TICK_INTERVAL)

        self._tick_timer.timeout.connect(self._run)

        self._count = 0

    def _update_target(self):
        self._count += 1
        if np.mod(self._count, self.TARGET_INTERVAL) == 0:
            try:
                self._target.position = next(self._route)
            except StopIteration:
                pass

            self._count = 0

    def _run(self):
        # Update regulator with data
        self._hexacopter.update()
        self._hexacopter.pitch, self._hexacopter.roll, _ = self._regulator.update(
            self._hexacopter.noisy_position, self._hexacopter.noisy_direction, self._target.position)

        self._update_target()
        self.update()


class Map(QLabel):
    def __init__(self, hexacopter_model, target):
        super().__init__()
        self.setMinimumSize(480, 480)

        self._hexacopter = HexacopterView(hexacopter_model)
        self._target = TargetView(target)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)

        view_size = Vector2D(self.geometry().width(), self.geometry().height())

        self._draw_background(painter, view_size)

        self._target.draw(painter, view_size)
        self._hexacopter.draw(painter, view_size)

    @staticmethod
    def _draw_background(painter, view_size):
        painter.setBrush(Qt.white)
        painter.setPen(Qt.white)
        painter.drawRect(0, 0, view_size.x, view_size.y)


class HexacopterView:
    def __init__(self, hexacopter_model):
        self.hexacopter_model = hexacopter_model

    def draw(self, painter, view_size):

        position_in_view = self.hexacopter_model.position * view_size
        direction_in_view = self.hexacopter_model.direction_vector * 0.01 * view_size
        traveling_direction_in_view = self.hexacopter_model.traveling_vector * 0.05 * view_size

        painter.setPen(Qt.black)
        painter.setBrush(Qt.red)

        main_radius = 5
        painter.drawEllipse(position_in_view.x - main_radius,
                            position_in_view.y - main_radius,
                            2 * main_radius, 2 * main_radius)

        main_radius = 3
        painter.drawEllipse(position_in_view.x + direction_in_view.x - main_radius,
                            position_in_view.y + direction_in_view.y - main_radius,
                            2 * main_radius, 2 * main_radius)

        main_radius = 2
        painter.drawEllipse(position_in_view.x + traveling_direction_in_view.x - main_radius,
                            position_in_view.y + traveling_direction_in_view.y - main_radius,
                            2 * main_radius, 2 * main_radius)


class Target:
    def __init__(self, position):
        self.position = position


class TargetView:
    def __init__(self, target):
        self.target = target

    def draw(self, painter, view_size):
        radius = 5

        position_in_view = self.target.position * view_size

        painter.setPen(Qt.black)
        painter.setBrush(Qt.blue)

        painter.drawEllipse(position_in_view.x - radius,
                            position_in_view.y - radius,
                            2 * radius, 2 * radius)


def main():
    app = QApplication([])
    win = HexacopterSimulator()
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
