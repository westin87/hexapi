import numpy as np
import sys

from hexacommon.common.coordinates import Vector2D
from hexacopter.utils.deriver import PDRegulator, Deriver


class HexacopterRegulator:
    def __init__(self, traveling_direction_alpha=0.6):

        self.speed_k = 2
        self.speed_td = 0.5

        self.traveling_direction_alpha = traveling_direction_alpha

        self.relative_direction_to_travel = 0

        self._traveling_direction_estimate = Vector2D()

        self._direction_deriver = Deriver(20)

        self.update_pd_regulator()

        self._counter = 0

    def update_pd_regulator(self):
        self._speed_regulator = PDRegulator(self.speed_k, self.speed_td)

    def update(self, position, direction, target_position):
        target_direction = _calculate_target_direction(position, target_position)

        relative_direction_to_travel = _calculate_relative_direction_to_go(
            direction, target_direction)

        pitch, roll = _direction_to_pitch_and_roll(
            relative_direction_to_travel)

        if np.isnan(pitch) or np.isnan(roll):
            pitch, roll = 0, 0

        speed = self._speed_regulator.update(
            target_position, position)

        return speed * pitch, speed * roll, 0


def _direction_to_pitch_and_roll(relative_direction_to_travel):
    pitch = np.cos(relative_direction_to_travel)
    roll = -np.sin(relative_direction_to_travel)
    return pitch, roll


def _calculate_relative_direction_to_go(direction, target_direction):
    base_suggestion = (np.arctan2(target_direction.x, target_direction.y) -
                       np.arctan2(direction.x, direction.y))

    return base_suggestion


def _calculate_target_direction(position, target_position):
    target_direction = target_position - position
    target_direction /= abs(target_direction)

    return target_direction
