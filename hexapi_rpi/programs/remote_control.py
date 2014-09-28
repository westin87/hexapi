import time

import programs.program as program


class RcProgram(program.Program):
    def __init__(self):
        super(RcProgram, self).__init__()

    def run(self):
        print "RC: Sarting RC program"
        while not self._stop_program:
            pass

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
        time.sleep(1)
        self._mov.set_pitch(0)
        self._mov.set_roll(0)
        self._mov.set_yaw(0)

    def register_callbacks(self, nh):
        nh.register_callback(self.set_pitch, "SET_PITCH")
        nh.register_callback(self.set_roll, "SET_ROLL")
        nh.register_callback(self.set_yaw, "SET_YAW")
        nh.register_callback(self.set_altitude, "SET_ALTITUDE")
        nh.register_callback(self.set_mode, "SET_MODE")
        nh.register_callback(self.start_motors, "START_MOTORS")
