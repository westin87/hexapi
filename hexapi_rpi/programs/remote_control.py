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

    def set_mode(self, level):
        self._mov.set_mode(int(level))

    def register_callbacks(self, nh):
        nh.register_callback(self.set_pitch, "SET_PITCH")
        nh.register_callback(self.set_roll, "SET_ROLL")
        nh.register_callback(self.set_yaw, "SET_YAW")
        nh.register_callback(self.set_altitude, "SET_ALTITUDE")
        nh.register_callback(self.set_mode, "SET_MODE")
