import numpy as np
import sys

from hexacommon.common.coordinates import Vector2D
from hexarpi.utils.deriver import PDRegulator, Deriver


class HexacopterRegulator:
    def __init__(self, position_alpha=0.1, direction_alpha=0.6, traveling_direction_alpha=0.6):

        self.yaw_k = .05
        self.yaw_td = .01
        self.pitch_k = 4
        self.pitch_td = 1

        self.position_alpha = position_alpha
        self.direction_alpha = direction_alpha
        self.traveling_direction_alpha = traveling_direction_alpha

        self._position_estimate = Vector2D(0, 0)
        self._direction_estimate = Vector2D(0, 0)
        self._traveling_direction_estimate = Vector2D(0, 0)

        self._direction_deriver = Deriver(20)

        self.create_new_pd_regulators()


    def set_initial_position(self, position):
        self._position_estimate = position

    def set_initial_direction(self, direction):
        self._direction_estimate = direction

    def create_new_pd_regulators(self):
        self.roll_regulator = PDRegulator(self.yaw_k, self.yaw_td)
        self.pitch_regulator = PDRegulator(self.pitch_k, self.pitch_td)

    def update(self, position, direction, target_position):
        self._update_position(position)
        self._update_direction_estimate(direction)
        self._update_traveling_direction_estimate()

        target_direction = self._calculate_target_direction(
            self._position_estimate, target_position)

        q = np.arccos(Vector2D.dot(self._traveling_direction_estimate, target_direction))
        if q > (np.pi / 2):
            pass  # Åker åt fel håll, vad göra?

        relative_direction_to_travel = self._calculate_relative_direction_to_go(
            self._direction_estimate, target_direction)

        roll, pitch = self._direction_to_pitch_and_roll(
            relative_direction_to_travel)

        return 0.4 * roll, 0.4 * pitch, 0

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

    def _update_traveling_direction_estimate(self):
        eps = sys.float_info.epsilon

        new_traveling_direction_estimate = self._direction_deriver.derive(self._position_estimate)
        new_traveling_direction_estimate /= abs(new_traveling_direction_estimate) + eps

        self._traveling_direction_estimate = (
            self.traveling_direction_alpha * new_traveling_direction_estimate +
            (1 - self.direction_alpha) * self._traveling_direction_estimate)

    @staticmethod
    def _calculate_target_direction(position, target_position):
        target_direction = target_position - position
        target_direction /= abs(target_direction)

        return target_direction

    @staticmethod
    def _calculate_relative_direction_to_go(direction, target_direction):
        return np.arccos(Vector2D.dot(direction, target_direction))

    @staticmethod
    def _direction_to_pitch_and_roll(relative_direction_to_travel):
        pitch = np.sin(relative_direction_to_travel)
        roll = np.cos(relative_direction_to_travel)
        return pitch, roll
