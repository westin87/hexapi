import numpy as np
from hexacommon.common.coordinates import Vector2D


class HexacopterModel:
    def __init__(self, position):
        self.position = position
        self.roll = 0
        self.pitch = 0
        self.yaw = 0
        self.direction = 0
        self.external_force = Vector2D(0, 0)

        self.traveling_vector = Vector2D(0, 0)

        self._speed_factor = 0.01
        self._noise_factor = 0.05

    @property
    def noisy_position(self):
        noise = Vector2D(2 * np.random.random() - 1, 2 * np.random.random() - 1)
        return self.position + (self._noise_factor * noise)

    @property
    def noisy_direction(self):
        noise = 2 * np.random.random() - 1
        return self.direction + (self._noise_factor * noise)

    @property
    def direction_vector(self):
        return Vector2D(np.cos(self.direction), np.sin(self.direction))

    def update(self):
        # Add external force
        self.position += self.external_force * self._speed_factor

        # Update direction
        self.direction += self.yaw

        # Calculate position change due to pitch
        pitch_delta = Vector2D(np.cos(self.direction) * self.pitch,
                               np.sin(self.direction) * self.pitch)

        pitch_delta *= self._speed_factor

        # Calculate position change due to roll
        roll_deta = Vector2D(np.cos(self.direction + (np.pi / 2)) * self.roll,
                             np.sin(self.direction + (np.pi / 2)) * self.roll)

        roll_deta *= self._speed_factor

        # Add pitch and roll position deltas to the current position
        movement_delta = pitch_delta + roll_deta

        self.traveling_vector = movement_delta / abs(movement_delta)

        self.position = self.position + movement_delta

    def __str__(self):
        return "Pos: {}, R: {}, P: {}, Y: {}".format(self.position, self.roll, self.pitch, self.yaw)
