import time
import pickle
import os
import platform
from hexacommon.common.coordinates import Point2D

from hexarpi.programs.program import Program
from hexarpi.utils import orientation

# Check if running on hexcopter or local, for special case setup
from hexarpi.utils.regulators import HexacopterRegulator

from hexacommon.constants import REGULATOR

rpi_hosts = ['hexapi', 'raspberrypi']
if platform.node() in rpi_hosts:
    print "RC: Running on RPI"
    user = "~pi"
else:
    print "RC: Running on local"
    user = "~"


class RcProgram(Program):
    def __init__(self, movement, network_handler, gps):
        super(RcProgram, self).__init__(movement, network_handler)

        self._use_regulator = False
        self._gps = gps
        self._orientation = orientation.Orientation()

        self._regulator = HexacopterRegulator()
        self._configure_regulator(self._regulator)

        self._regulator.set_initial_position(
            self._parse_gps_position(self._gps.get_gps_data()))

        self._log_file_path = ""
        self._log_data = dict()

        self._log_sensor_data = False

        self._target_position = Point2D(0, 0)

    def run(self):
        print "RC: Starting RC program"
        self._stop_program = False
        while not self._stop_program:
            gps_data = self._gps.get_gps_data()
            self._nh.send_command("GPS_DATA", gps_data)

            if self._log_sensor_data:
                self._log_sensor_data()

            if self._use_regulator:
                current_position = self._parse_gps_position(gps_data)

                pitch, yaw = self._regulator.update(
                    current_position, self._target_position)

                self._mov.set_pitch(pitch)
                self._mov.set_yaw(yaw)

            time.sleep(0.1)
        self._gps.kill()

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
        print "Starting engines"
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
            self._gps.get_gps_data())

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

        print "RC: Starting logging to {}".format(self._log_file_path)

    def stop_logging(self):
        self._log_sensor_data = False
        time.sleep(0.2)

        with open(self._log_file_path, 'w') as file_object:
            pickle.dump(self._log_data, file_object)

        print "RC: Done with logging"

    def _log_sensor_data(self):
        self._log_data['gps'].append(
            self._gps.get_gps_data())
        self._log_data['mag'].append(
            self._orientation.get_magnetic_field())
        self._log_data['acc'].append(
            self._orientation.get_acceleration())
        self._log_data['ang'].append(
            self._orientation.get_angular_rate())

    @staticmethod
    def _configure_regulator(regulator):
        regulator.yaw_k = REGULATOR.YAW_K
        regulator.yaw_td = REGULATOR.YAW_TD
        regulator.pitch_k = REGULATOR.PITCH_K
        regulator.pitch_td = REGULATOR.PITCH_TD

    @staticmethod
    def _parse_gps_position(gps_data):
        current_position = Point2D(
            float(gps_data.data['latitude']),
            float(gps_data.data['longitude']))

        return current_position

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
    user_home = os.path.expanduser(user)
    log_dir = os.path.join(user_home, "hexapi_logs")

    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    return os.path.join(log_dir, filename)
