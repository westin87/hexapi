import numpy as np
import sys

from hexacommon.common.coordinates import Vector2D
from hexacopter.utils.deriver import PDRegulator, Deriver


class HexacopterRegulator:
    def __init__(self, position_alpha=0.1, direction_alpha=0.6, traveling_direction_alpha=0.6):

        self.speed_k = 2
        self.speed_td = 0.5

        self.position_alpha = position_alpha
        self.direction_alpha = direction_alpha
        self.traveling_direction_alpha = traveling_direction_alpha

        self.relative_direction_to_travel = 0

        self._position_estimate = Vector2D(0, 0)
        self._direction_estimate = Vector2D(0, 0)
        self._traveling_direction_estimate = Vector2D(0, 0)

        self._direction_deriver = Deriver(20)

        self.update_pd_regulator()

        self._counter = 0

    def set_initial_position(self, position):
        self._position_estimate = position

    def set_initial_direction(self, direction):
        self._direction_estimate = direction

    def update_pd_regulator(self):
        self._speed_regulator = PDRegulator(self.speed_k, self.speed_td)

    def update(self, position, direction, target_position):
        self._update_position(position)
        self._update_direction_estimate(direction)
        self._update_traveling_direction_estimate()

        target_direction = _calculate_target_direction(
            self._position_estimate, target_position)

        relative_direction_to_travel = _calculate_relative_direction_to_go(
            self._direction_estimate, target_direction)

        pitch, roll = _direction_to_pitch_and_roll(
            relative_direction_to_travel)

        speed = self._speed_regulator.update(
            target_position, self._position_estimate)

        return speed * pitch, speed * roll, 0

    def _update_position(self, new_position):

        self._position_estimate = (
            self.position_alpha * new_position +
            (1 - self.position_alpha) * self._position_estimate)

    def _update_direction_estimate(self, new_direction):
        new_direction = Vector2D(np.cos(new_direction), np.sin(new_direction))

        self._direction_estimate = (
            self.direction_alpha * new_direction +
            (1 - self.direction_alpha) * self._direction_estimate)

        self._direction_estimate /= abs(new_direction)

        self._direction_estimate = new_direction

    def _update_traveling_direction_estimate(self):
        eps = sys.float_info.epsilon

        new_traveling_direction_estimate = self._direction_deriver.derive(self._position_estimate)
        new_traveling_direction_estimate /= abs(new_traveling_direction_estimate) + eps

        self._traveling_direction_estimate = (
            self.traveling_direction_alpha * new_traveling_direction_estimate +
            (1 - self.direction_alpha) * self._traveling_direction_estimate)


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
