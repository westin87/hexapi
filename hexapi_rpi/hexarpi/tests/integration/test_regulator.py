import sys

from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout

from hexacommon.common.coordinates import Vector2D
from hexarpi.tests.integration.hexacopter_model import HexacopterModel
from hexarpi.utils.regulator_prototype import HexacopterRegulator


class HexacopterSimulator(QWidget):
    def __init__(self):
        super().__init__()

        start_position = Vector2D(0.5, 0.5)

        self.regulator = HexacopterRegulator()
        self.regulator.set_initial_position(start_position)

        self.hexacopter = HexacopterModel(start_position)
        self.hexacopter.external_force = Vector2D(0, 0.04)

        self.target = Target(Vector2D(0.8, 0.3))

        self.map = Map(self.hexacopter, self.target)

        layout = QVBoxLayout()
        layout.addWidget(self.map)
        self.setLayout(layout)

        self.timer = QTimer()
        self.timer.start(25)

        self.timer.timeout.connect(self.run)

    def run(self):
        # Update regulator with data
        self.hexacopter.update()
        self.hexacopter.roll, self.hexacopter.pitch, self.hexacopter.yaw = self.regulator.update(
            self.hexacopter.position, self.hexacopter.direction, self.target.position)

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

        self._hexacopter.draw(painter, view_size)
        self._target.draw(painter, view_size)

    @staticmethod
    def _draw_background(painter, view_size):
        painter.setBrush(Qt.white)
        painter.setPen(Qt.white)
        painter.drawRect(0, 0, view_size.x, view_size.y)


class HexacopterView:
    def __init__(self, hexacopter_model):
        self.hexacopter_model = hexacopter_model

    def draw(self, painter, view_size):
        radius = 5

        position_in_view = self.hexacopter_model.position * view_size

        painter.setPen(Qt.black)
        painter.setBrush(Qt.red)

        painter.drawEllipse(position_in_view.x - radius,
                            position_in_view.y - radius,
                            2 * radius, 2 * radius)


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


if __name__ == '__main__':
    app = QApplication([])
    win = HexacopterSimulator()
    win.show()
    sys.exit(app.exec_())
