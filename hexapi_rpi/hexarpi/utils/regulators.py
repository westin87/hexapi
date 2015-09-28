import math
import sys

import numpy as np

from hexacommon.common.coordinates import Point2D
from hexarpi.utils.deriver import Deriver


class PDRegulator:
    def __init__(self, K, Td):
        self._k = K
        self._td = Td

        self._deriver = Deriver(10)

    def update(self, R, Y):
        u = self._k * (R - Y) + self._td * self._deriver.derive(R - Y)

        u = abs(u)
        return np.clip(u, -0.5, 0.5)


class HexacopterRegulator:
    def __init__(self):
        self.position_estimate = Point2D(0, 0)
        self.direction_estimate = Point2D(0, 0)

        self._deriver = Deriver(10)

    def set_initial_position(self, position):
        self.position_estimate = position

    def _update_position_and_direction_estimate(self, new_position):
        alpha = 0.1

        self.position_estimate = (
            alpha * new_position + (1 - alpha) * self.position_estimate)

        self._update_direction_estimate()

    def _update_direction_estimate(self):
        eps = sys.float_info.epsilon
        alpha = 0.6

        new_direction_estimate = self._deriver.derive(self.position_estimate)
        new_direction_estimate /= abs(new_direction_estimate) + eps

        self.direction_estimate = (
            alpha * new_direction_estimate +
            (1 - alpha) * self.direction_estimate)

    def _calculate_target_direction(self, target_position):
            target_direction = target_position - self.position_estimate
            target_direction /= abs(target_direction)

            return target_direction

    def update(self, position, target_position):
        self._update_position_and_direction_estimate(position)

        target_direction = self._calculate_target_direction(target_position)

        angle_to_target = math.acos(
            Point2D.dot(self.direction_estimate, target_direction))

        target_direction_perp = Point2D(-target_direction.y, target_direction.x)

        projection = Point2D.dot(
            self.direction_estimate,
            target_direction_perp / abs(target_direction_perp))

        yaw_regulator = PDRegulator(.05, .01)
        yaw = (-math.copysign(1, projection) *
               yaw_regulator.update(target_direction, self.direction_estimate))

        pitch_regulator = PDRegulator(4, 1)
        pitch = pitch_regulator.update(target_position, self.position_estimate)

        return pitch, yaw
