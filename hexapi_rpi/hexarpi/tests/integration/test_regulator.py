import time
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation

import numpy as np

from hexacommon.common.coordinates import Point2D
from hexarpi.tests.integration.hexacopter_model import HexacopterModel
from hexarpi.utils.regulators import HexacopterRegulatorPrototype


class TestRegulator:
    def __init__(self):
        start_position = Point2D(0.5, 0.5)
        self.target_position = Point2D(0.8, 0.3)

        self.copter = HexacopterModel(start_position)

        self.regulator = HexacopterRegulatorPrototype()
        self.regulator.set_initial_position(start_position)

        self.copter.external_force = Point2D(0, 0.04)

        self.fig, ax = plt.subplots()
        ax.set_ylim([0, 1])
        ax.set_xlim([0, 1])

        # Plot target position
        self.target = ax.plot(self.target_position.x, self.target_position.y, "ob").pop()

        # Plot copter position and direction
        self.copter_position = self.create_point(ax, self.copter.position, 'or')
        self.direction = ax.plot(self.copter.position.x, self.copter.position.y, "og").pop()

        # Plot estimated copter position and direction
        self.estimate_copter_position = ax.plot(self.copter.position.x, self.copter.position.y, "sr").pop()
        self.estimate_direction = ax.plot(self.copter.position.x, self.copter.position.y, "sg").pop()

    @staticmethod
    def create_point(axis, position, type="or"):
        return axis.plot(position.x, position.y, type).pop()

    def iterate(self, i):

        # Change target after 300 iterations
        if i == 300:
            self.target_position = Point2D(0.2, 0.6)
            self.target.set_xdata(self.target_position.x)
            self.target.set_ydata(self.target_position.y)

        # Update regulator with data
        self.copter.update()
        self.copter.roll, self.copter.pitch, self.copter.yaw = self.regulator.update(
            self.copter.noisy_position, self.target_position)

        # Update copter position and direction
        self.copter_position.set_xdata(self.copter.position.x)
        self.copter_position.set_ydata(self.copter.position.y)
        self.direction.set_xdata(self.copter.position.x + self.copter.direction_vector.x / 100)
        self.direction.set_ydata(self.copter.position.y + self.copter.direction_vector.y / 100)

        # Update estimated copter position and direction
        self.estimate_copter_position.set_xdata(self.regulator._position_estimate.x)
        self.estimate_copter_position.set_ydata(self.regulator._position_estimate.y)
        self.estimate_direction.set_xdata(
            self.regulator._position_estimate.x + self.regulator._direction_estimate.x / 100)
        self.estimate_direction.set_ydata(
            self.regulator._position_estimate.y + self.regulator._direction_estimate.y / 100)

    def run(self):
        ani = FuncAnimation(self.fig, self.iterate, frames=600, interval=25, repeat=False)
        plt.show()

test = TestRegulator()
test.run()

