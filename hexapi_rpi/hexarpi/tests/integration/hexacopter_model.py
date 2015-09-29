import numpy as np
from hexacommon.common.coordinates import Point2D


class HexacopterModel:
    def __init__(self, position):
        self.position = position
        self.direction_vector = Point2D(0, 0)
        self.roll = 0
        self.pitch = 0
        self.yaw = 0
        self.direction = np.random.random()
        self.external_force = Point2D(0, 0)

        self._speed_factor = 0.01
        self._noise_factor = 0.02

    @property
    def noisy_position(self):
        noise = Point2D(2 * np.random.random() - 1, 2 * np.random.random() - 1)
        return self.position + (self._noise_factor * noise)

    @property
    def direction(self):
        return self.__direction / (2 * np.pi)

    @direction.setter
    def direction(self, new_direction):
        self.__direction = np.mod((2 * np.pi) * new_direction, 2 * np.pi)

    def update(self):
        # Add external force
        self.position += self.external_force * self._speed_factor

        # Update direction
        self.__direction += self.yaw

        self.direction_vector = Point2D(np.cos(self.__direction),
                                        np.sin(self.__direction))

        # Calculate position change due to pitch
        pitch_delta = Point2D(np.cos(self.__direction) * self.pitch,
                              np.sin(self.__direction) * self.pitch)

        pitch_delta *= self._speed_factor

        # Calculate position change due to roll
        roll_deta = Point2D(np.cos(self.__direction + (np.pi / 2)) * self.roll,
                            np.sin(self.__direction + (np.pi / 2)) * self.roll)

        roll_deta *= self._speed_factor

        # Add pitch and roll position deltas to the current position
        self.position = self.position + pitch_delta + roll_deta

    def __str__(self):
        return "Pos: {}, R: {}, P: {}, Y: {}".format(self.position, self.roll, self.pitch, self.yaw)
