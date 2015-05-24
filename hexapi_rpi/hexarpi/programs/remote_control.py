import time
from pathlib import Path
import pickle

from hexarpi.programs import program
from hexarpi.utils import gps_util
from hexarpi.utils import orientation


class RcProgram(program.Program):
    def __init__(self, nh):
        super(RcProgram, self).__init__()
        self.__gps = gps_util.GPSUtil()
        self.__orientation = orientation.Orientation()
        self.__nh = nh

        self.__log_file_path = Path()
        self.__log_interval = 0.1
        self.__log_data = dict()

        self.__log_sensor_data = False

    def run(self):
        print "RC: Starting RC program"
        self._stop_program = False
        while not self._stop_program:
            if self.__log_sensor_data:
                self.__log_data['gps'] = self.__gps.get_gps_data()
                self.__log_data['mag'] = self.__orientation.get_magnetic_field()
                self.__log_data['acc'] = self.__orientation.get_acceleration()
                self.__log_data['ang'] = self.__orientation.get_angular_rate()
                time.sleep(self.__log_interval)

            time.sleep(0.01)
        self.__gps.kill()

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
        self._mov.set_pitch(-100)
        self._mov.set_roll(-100)
        self._mov.set_yaw(-100)
        self._mov.set_altitude(-100)
        time.sleep(1)
        self._mov.set_pitch(0)
        self._mov.set_roll(0)
        self._mov.set_yaw(0)
        self._mov.set_altitude(-75)

    def start_logging(self, file_tag, log_interval="0.1"):
        self.__log_interval = float(log_interval)
        self.__log_sensor_data = True

        timestamp = time.strftime("%y%m%d%H%M%S")
        filename = "{}_{}.bin".format(timestamp, file_tag)

        self.__log_file_path = Path(__file__).parent.parent / filename
        self.__log_data = dict()

    def stop_logging(self):
        self.__log_sensor_data = False
        time.sleep(0.2)

        with self.__log_file_path.open('w') as file_object:
            pickle.dump(self.__log_data, file_object)

    def register_callbacks(self):
        self.__nh.register_callback(self.set_pitch, "SET_PITCH")
        self.__nh.register_callback(self.set_roll, "SET_ROLL")
        self.__nh.register_callback(self.set_yaw, "SET_YAW")
        self.__nh.register_callback(self.set_altitude, "SET_ALTITUDE")
        self.__nh.register_callback(self.set_mode, "SET_MODE")
        self.__nh.register_callback(self.start_motors, "START_MOTORS")
        self.__nh.register_callback(self.start_logging, "START_LOGGING")
        self.__nh.register_callback(self.stop_logging, "STOP_LOGGING")
