from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation

import numpy as np

from hexacommon.common.coordinates import Point2D
from hexarpi.tests.integration.hexacopter_model import HexacopterModel
from hexarpi.utils.regulators import HexacopterRegulator


target_position = Point2D(0.8, 0.3)
start_position = Point2D(0.5, 0.5)

copter = HexacopterModel(start_position)
regulator = HexacopterRegulator()
regulator.set_initial_position(start_position)
copter.pitch = 0.1
copter.external_force = Point2D(0, 0.04)

fig, ax = plt.subplots()
ax.set_ylim([0, 1])
ax.set_xlim([0, 1])

target = ax.plot(target_position.x, target_position.y, "ob").pop()

copter_position = ax.plot(copter.position.x, copter.position.y, "or").pop()
direction = ax.plot(copter.position.x, copter.position.y, "og").pop()

estimate_copter_position = ax.plot(copter.position.x, copter.position.y, "sr").pop()
estimate_direction = ax.plot(copter.position.x, copter.position.y, "sg").pop()

def animate(i):
    print(i, flush=True)

    if i > 300:
        target_position = Point2D(0.2, 0.6)
        target.set_xdata(target_position.x)
        target.set_ydata(target_position.y)
    else:
        target_position = Point2D(0.8, 0.3)

    copter.update()
    copter.pitch, copter.yaw = regulator.update(copter.noisy_position, target_position)

    print(copter, flush=True)

    copter_position.set_xdata(copter.position.x)
    copter_position.set_ydata(copter.position.y)
    direction.set_xdata(copter.position.x + copter.direction_vector.x / 100)
    direction.set_ydata(copter.position.y + copter.direction_vector.y / 100)

    estimate_copter_position.set_xdata(regulator._position_estimate.x)
    estimate_copter_position.set_ydata(regulator._position_estimate.y)
    estimate_direction.set_xdata(regulator._position_estimate.x + regulator._direction_estimate.x / 100)
    estimate_direction.set_ydata(regulator._position_estimate.y + regulator._direction_estimate.y / 100)

ani = FuncAnimation(fig, animate, np.arange(1, 600), interval=25, repeat=False)
plt.show()
