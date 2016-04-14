import numpy as np
import sys

from hexacommon.common.coordinates import Vector2D
from hexarpi.utils.deriver import PDRegulator, Deriver


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

        self.create_new_pd_regulators()

    def set_initial_position(self, position):
        self._position_estimate = position

    def set_initial_direction(self, direction):
        self._direction_estimate = direction

    def create_new_pd_regulators(self):
        self.speed_regulator = PDRegulator(self.speed_k, self.speed_td)

    def update(self, position, direction, target_position):
        self._update_position(position)
        self._update_direction_estimate(direction)
        self._update_traveling_direction_estimate()

        target_direction = self._calculate_target_direction(
            self._position_estimate, target_position)

        relative_direction_to_travel = self._calculate_relative_direction_to_go(
            self._direction_estimate, target_direction)

        roll, pitch = self._direction_to_pitch_and_roll(
            relative_direction_to_travel)

        speed = self.speed_regulator.update(
            target_position, self._position_estimate)

        return speed * roll, speed * pitch, 0

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

    @staticmethod
    def _calculate_target_direction(position, target_position):
        target_direction = target_position - position
        target_direction /= abs(target_direction)

        return target_direction

    @staticmethod
    def _calculate_relative_direction_to_go(direction, target_direction):
        print("." * 20)
        base_suggestion = np.arccos(Vector2D.dot(direction, target_direction))
        suggestion_2 = np.pi + base_suggestion
        suggestion_3 = np.pi - base_suggestion

        if HexacopterRegulator._is_new_direction_correct(
                direction, base_suggestion, target_direction):
            print("A")
            relative_travel_angle = base_suggestion
        elif HexacopterRegulator._is_new_direction_correct(
                direction, suggestion_2, target_direction):
            print("B")
            relative_travel_angle = suggestion_2
        elif HexacopterRegulator._is_new_direction_correct(
                direction, suggestion_3, target_direction):
            print("C")
            relative_travel_angle = suggestion_3
        else:
            print("Could not find a direction to go!")
            relative_travel_angle = 0
            while not (HexacopterRegulator._is_new_direction_correct(
                direction, relative_travel_angle, target_direction)):
                relative_travel_angle += 0.1

        return relative_travel_angle

    @staticmethod
    def _is_new_direction_correct(direction, relative_travel_angle, target_direction):
        x_unit_vector = Vector2D(x=1, y=0)
        angle_to_unit_vector = np.arccos(Vector2D.dot(direction, x_unit_vector))
        travel_angle_from_unit_vector = relative_travel_angle - angle_to_unit_vector

        new_traveling_direction = Vector2D(
            x=np.cos(travel_angle_from_unit_vector), y=np.sin(travel_angle_from_unit_vector))

        target_direction /= abs(target_direction)
        new_traveling_direction /= abs(new_traveling_direction)

        print(abs(target_direction - new_traveling_direction))

        return abs(target_direction - new_traveling_direction) < 0.5

    @staticmethod
    def _direction_to_pitch_and_roll(relative_direction_to_travel):
        pitch = np.sin(relative_direction_to_travel)
        roll = np.cos(relative_direction_to_travel)
        return pitch, roll
