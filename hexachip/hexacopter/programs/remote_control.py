import logging
import os
import pickle
import time

from hexacommon.common.communication import Communication
from hexacommon.common.coordinates import Point2D
from hexacommon.constants import REGULATOR
from hexacopter.programs.baseprogram import BaseProgram
from hexacopter.utils.regulator import HexacopterRegulator
from hexacopter.utils.position import Position
from hexacopter.utils.movement import Movement
from hexacopter.utils.orientation import Orientation


class RcProgram(BaseProgram):
    def __init__(self, communication, movement, position, orientation):
        """
        :param Communication communication:
        :param Movement movement:
        :param Position position:
        :param Orientation orientation:
        """
        super().__init__(communication, movement)

        self._position = position
        self._orientation = orientation

        self._use_regulator = False
        self._regulator = HexacopterRegulator()
        self._configure_regulator(self._regulator)

        self._regulator.set_initial_position(self._position.position)

        self._log_file_path = ""
        self._log_sensor_data = False
        self._log_data = dict()

        self._target_position = Point2D(0, 0)

        self._connect_callbacks()

        self._send_cunter = 0

    def run(self):
        logging.info("RC: Starting RC program")
        self._stop_program = False
        while not self._stop_program:
            self._send_cunter += 1
            if self._send_cunter % 5 == 0:
                self._communication.send_command("GPS_DATA", self._position.latitude, self._position.longitude)
                self._send_cunter = 0

            if self._log_sensor_data:
                self._log_sensor_data()

            if self._use_regulator:
                pitch, roll, yaw = self._regulator.update(
                    self._position.position, self._orientation.direction, self._target_position)

                pitch = int(100 * pitch)
                roll = int(100 * roll)
                yaw = int(100 * yaw)

                logging.debug("RC: Setting pitch: {}, roll: {}, yaw: {}".format(
                    pitch, roll, yaw))

                self._move.set_pitch(pitch)
                self._move.set_roll(roll)
                self._move.set_yaw(yaw)

            time.sleep(0.1)

    def set_pitch(self, level):
        self._move.set_pitch(int(level))

    def set_roll(self, level):
        self._move.set_roll(int(level))

    def set_yaw(self, level):
        self._move.set_yaw(int(level))

    def set_altitude(self, level):
        self._move.set_altitude(int(level))

    def set_mode(self, mode):
        mode_trans = {"MAN": -50, "FS": -15, "ATTI": 20}
        self._move.set_mode(mode_trans[mode])

    def start_motors(self):
        logging.info("Starting engines")
        self._move.set_pitch(-100)
        self._move.set_roll(-100)
        self._move.set_yaw(-100)
        self._move.set_altitude(-100)
        time.sleep(1)
        self._move.set_pitch(0)
        self._move.set_roll(0)
        self._move.set_yaw(0)
        self._move.set_altitude(-75)

    def start_regulator(self):
        logging.info("RC: Starting regulator")
        self._target_position = self._position.position

        self._use_regulator = True

    def stop_regulator(self):
        logging.info("RC: Stopping regulator")
        self._use_regulator = False

        time.sleep(0.5)
        self._move.set_pitch(0)
        self._move.set_yaw(0)

    def set_target_position(self, latitude, longitude):
        logging.info("RC: Setting target position, lat: {}, long: {}".format(
            latitude, longitude))

        self._target_position = Point2D(float(latitude), float(longitude))

    def set_regulator_parameters(self, speed_k, speed_td):
        logging.info("RC: Setting regulator settings, K: {}, Td: {}".format(
            speed_k, speed_td))

        if speed_k and speed_td:
            self._regulator.speed_k = float(speed_k)
            self._regulator.speed_td = float(speed_td)
            self._regulator.update_pd_regulator()

    def start_logging(self, file_tag):
        self._log_sensor_data = True

        timestamp = time.strftime("%y%m%d%H%M%S")
        filename = "{}_{}.bin".format(timestamp, file_tag)

        self._log_file_path = _prepare_logging_path(filename)

        self._log_data = dict()
        self._log_data['gps'] = []
        self._log_data['mag'] = []
        self._log_data['acc'] = []
        self._log_data['ang'] = []

        logging.info("RC: Starting sensor logging to {}".format(self._log_file_path))

    def stop_logging(self):
        self._log_sensor_data = False
        time.sleep(0.2)

        with open(self._log_file_path, 'w') as file_object:
            pickle.dump(self._log_data, file_object)

        logging.info("RC: Sensor logging finished")

    def _log_sensor_data(self):
        self._log_data['gps'].append(
            self._position.position)

    @staticmethod
    def _configure_regulator(regulator):
        regulator.speed_k = REGULATOR.SPEED_K
        regulator.speed_td = REGULATOR.SPEED_TD
        regulator.update_pd_regulator()

    def _connect_callbacks(self):
        self._communication.connect_command_callback(self.set_pitch, "SET_PITCH")
        self._communication.connect_command_callback(self.set_roll, "SET_ROLL")
        self._communication.connect_command_callback(self.set_yaw, "SET_YAW")
        self._communication.connect_command_callback(self.set_altitude, "SET_ALTITUDE")
        self._communication.connect_command_callback(self.set_mode, "SET_MODE")
        self._communication.connect_command_callback(self.start_motors, "START_MOTORS")
        self._communication.connect_command_callback(self.start_logging, "START_LOGGING")
        self._communication.connect_command_callback(self.stop_logging, "STOP_LOGGING")
        self._communication.connect_command_callback(self.start_regulator, "START_REGULATOR")
        self._communication.connect_command_callback(self.stop_regulator, "STOP_REGULATOR")
        self._communication.connect_command_callback(self.set_regulator_parameters, "SET_REG_PARAMS")
        self._communication.connect_command_callback(self.set_target_position, "SET_TARGET_POSITION")


def _prepare_logging_path(filename):
    user_home = os.path.expanduser("~")
    log_dir = os.path.join(user_home, "hexapi_logs")

    os.makedirs(log_dir, exist_ok=True)

    return os.path.join(log_dir, filename)
