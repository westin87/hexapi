from programs.program import Program


class GpsProgram(Program):
    def __init__(self):
        super(GpsProgram, self).__init__()

    def run(self):
        print "GP: Sarting GPS program"
        while not self._stop_program:
            # if not at_gps_pos:
            #     fly_to_gps_pos()
            pass

    def set_pitch(self, level):
        self._mov.set_pitch(int(level))

    def set_roll(self, level):
        self._mov.set_roll(int(level))

    def set_yaw(self, level):
        self._mov.set_yaw(int(level))

    def set_altitude(self, level):
        self._mov.set_altitude(int(level))

    def register_callbacks(self, nh):
        nh.register_callback(self.set_pitch, "SET_PITCH")
        nh.register_callback(self.set_roll, "SET_ROLL")
        nh.register_callback(self.set_yaw, "SET_YAW")
        nh.register_callback(self.set_altitude, "SET_ALTITUDE")
