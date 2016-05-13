import logging
import os
import pickle
import time

from hexacommon.common.network_handler import NetworkHandler
from hexacommon.common.coordinates import Point2D
from hexacommon.constants import REGULATOR
from hexarpi.programs.program import Program
from hexarpi.utils.regulator import HexacopterRegulator
from hexarpi.utils.position import Position
from hexarpi.utils.movement import Movement
from hexarpi.utils.orientation import Orientation


class RcProgram(Program):
    def __init__(self, network_handler, movement, position, orientation):
        """
        :param NetworkHandler network_handler:
        :param Movement movement:
        :param Position position:
        :param Orientation orientation:
        """
        super().__init__(network_handler, movement)

        self._position = position
        self._orientation = orientation

        self._use_regulator = False
        self._regulator = HexacopterRegulator()
        self._configure_regulator(self._regulator)

        self._regulator.set_initial_position(self._position.position)

        self._log_file_path = ""
        self._log_data = dict()

        self._log_sensor_data = False

        self._target_position = Point2D(0, 0)

    def run(self):
        logging.info("RC: Starting RC program")
        self._stop_program = False
        while not self._stop_program:
            self._nh.send_command("GPS_DATA", self._position.latitude, self._position.longitude)

            if self._log_sensor_data:
                self._log_sensor_data()

            if self._use_regulator:
                current_position = self._position.position

                roll, pitch, yaw = self._regulator.update(
                    current_position, self._target_position)

                self._mov.set_roll(roll)
                self._mov.set_pitch(pitch)
                self._mov.set_yaw(yaw)

            time.sleep(0.1)
        self._position.kill()

    def set_pitch(self, level):
        self._mov.set_pitch(int(level))

    def set_roll(self, level):
        self._mov.set_roll(int(level))

    def set_yaw(self, level):
        self._mov.set_yaw(int(level))

    def set_altitude(self, level):
        self._mov.set_altitude(int(level))

    def set_mode(self, mode):
        mode_trans = {"MAN": -50, "FS": -15, "ATTI": 20}
        self._mov.set_mode(mode_trans[mode])

    def start_motors(self):
        logging.info("Starting engines")
        self._mov.set_pitch(-100)
        self._mov.set_roll(-100)
        self._mov.set_yaw(-100)
        self._mov.set_altitude(-100)
        time.sleep(1)
        self._mov.set_pitch(0)
        self._mov.set_roll(0)
        self._mov.set_yaw(0)
        self._mov.set_altitude(-75)

    def start_regulator(self):
        self._target_position = self._parse_gps_position(
            self._position.get_gps_data())

        self._use_regulator = True

    def stop_regulator(self):
        self._use_regulator = False

        time.sleep(0.5)
        self._mov.set_pitch(0)
        self._mov.set_yaw(0)

    def set_target_position(self, latitude, longitude):
        self._target_position = Point2D(float(latitude), float(longitude))

    def set_regulator_parameters(self, yaw_k, yaw_td, pitch_k, pitch_td):
        self._regulator.yaw_k = float(yaw_k)
        self._regulator.yaw_td = float(yaw_td)
        self._regulator.pitch_k = float(pitch_k)
        self._regulator.pitch_td = float(pitch_td)

        self._regulator.create_new_pd_regulators()

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

        logging.info("RC: Starting logging to {}".format(self._log_file_path))

    def stop_logging(self):
        self._log_sensor_data = False
        time.sleep(0.2)

        with open(self._log_file_path, 'w') as file_object:
            pickle.dump(self._log_data, file_object)

        logging.info("RC: Done logging")

    def _log_sensor_data(self):
        self._log_data['gps'].append(
            self._position.position)

    @staticmethod
    def _configure_regulator(regulator):
        regulator.speed_k = REGULATOR.SPEED_K
        regulator.speed_td = REGULATOR.SPEED_TD

    def register_callbacks(self):
        self._nh.register_callback(self.set_pitch, "SET_PITCH")
        self._nh.register_callback(self.set_roll, "SET_ROLL")
        self._nh.register_callback(self.set_yaw, "SET_YAW")
        self._nh.register_callback(self.set_altitude, "SET_ALTITUDE")
        self._nh.register_callback(self.set_mode, "SET_MODE")
        self._nh.register_callback(self.start_motors, "START_MOTORS")
        self._nh.register_callback(self.start_logging, "START_LOGGING")
        self._nh.register_callback(self.stop_logging, "STOP_LOGGING")
        self._nh.register_callback(self.start_regulator, "START_REGULATOR")
        self._nh.register_callback(self.stop_regulator, "STOP_REGULATOR")
        self._nh.register_callback(
            self.set_regulator_parameters, "SET_REG_PARAMS")
        self._nh.register_callback(
            self.set_target_position, "SET_TARGET_POSITION")


def _prepare_logging_path(filename):
    user_home = os.path.expanduser("~")
    log_dir = os.path.join(user_home, "hexapi_logs")

    os.makedirs(log_dir, exist_ok=True)

    return os.path.join(log_dir, filename)
