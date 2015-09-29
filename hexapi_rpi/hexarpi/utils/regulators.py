import math
import sys

import numpy as np

from hexacommon.common.coordinates import Point2D
from hexarpi.utils.deriver import Deriver


class PDRegulator:
    def __init__(self, k, td, samples=20):
        self.k = k
        self.td = td

        self._deriver = Deriver(samples)

    def update(self, R, Y):
        u = self.k * (R - Y) + self.td * self._deriver.derive(R - Y)
        u = abs(u)

        return np.clip(u, -0.5, 0.5)


class HexacopterRegulator:
    def __init__(self, position_alpha=0.1, direction_alpha=0.6, samples=20):

        self.yaw_k = .05
        self.yaw_td = .01
        self.pitch_k = 4
        self.pitch_td = 1

        self.position_alpha = position_alpha
        self.direction_alpha = direction_alpha

        self._position_estimate = Point2D(0, 0)
        self._direction_estimate = Point2D(0, 0)

        self._deriver = Deriver(samples)

        self.yaw_regulator = PDRegulator(self.yaw_k, self.yaw_td)
        self.pitch_regulator = PDRegulator(self.pitch_k, self.pitch_td)

    def set_initial_position(self, position):
        self._position_estimate = position

    def _update_position_and_direction_estimate(self, new_position):

        self._position_estimate = (
            self.position_alpha * new_position +
            (1 - self.position_alpha) * self._position_estimate)

        self._update_direction_estimate()

    def _update_direction_estimate(self):
        eps = sys.float_info.epsilon

        new_direction_estimate = self._deriver.derive(self._position_estimate)
        new_direction_estimate /= abs(new_direction_estimate) + eps

        self._direction_estimate = (
            self.direction_alpha * new_direction_estimate +
            (1 - self.direction_alpha) * self._direction_estimate)

    def _calculate_target_direction(self, target_position):
            target_direction = target_position - self._position_estimate
            target_direction /= abs(target_direction)

            return target_direction

    def _calculate_angle_to_target(self, target_direction):
        return math.acos(Point2D.dot(self._direction_estimate, target_direction))

    def _calculate_turning_direction(self, target_direction):
        orthogonal_target_direction = Point2D(-target_direction.y,
                                              target_direction.x)

        projection = Point2D.dot(
            self._direction_estimate,
            orthogonal_target_direction / abs(orthogonal_target_direction))

        return -math.copysign(1, projection)

    def update(self, position, target_position):
        self._update_position_and_direction_estimate(position)

        target_direction = self._calculate_target_direction(target_position)

        direction = self._calculate_turning_direction(target_direction)

        yaw = direction * self.yaw_regulator.update(
            target_direction, self._direction_estimate)

        pitch = self.pitch_regulator.update(
            target_position, self._position_estimate)

        return pitch, yaw
