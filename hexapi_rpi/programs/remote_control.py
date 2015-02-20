import time

from programs import program
from utils import gps_util
from utils import orientation


class RcProgram(program.Program):
    def __init__(self, nh):
        super(RcProgram, self).__init__()
        self.__gps = gps_util.GPSUtil()
        self.__orientation = orientation.Orientation()
        self.__nh = nh

    def run(self):
        print "RC: Starting RC program"
        self._stop_program = False
        while not self._stop_program:
            gps_data = self.__gps.get_gps_data()
            self.__nh.send_command("GPS_DATA", gps_data)

            mag_data = self.__orientation.get_magnetic_field()
            self.__nh.send_command("MAG_DATA", mag_data)

            acc_data = self.__orientation.get_acceleration()
            self.__nh.send_command("ACC_DATA", acc_data)

            ang_data = self.__orientation.get_angular_rate()
            self.__nh.send_command("ANG_DATA", ang_data)

            time.sleep(1)

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

    def register_callbacks(self):
        self.__nh.register_callback(self.set_pitch, "SET_PITCH")
        self.__nh.register_callback(self.set_roll, "SET_ROLL")
        self.__nh.register_callback(self.set_yaw, "SET_YAW")
        self.__nh.register_callback(self.set_altitude, "SET_ALTITUDE")
        self.__nh.register_callback(self.set_mode, "SET_MODE")
        self.__nh.register_callback(self.start_motors, "START_MOTORS")
