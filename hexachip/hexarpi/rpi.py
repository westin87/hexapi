import logging

import signal
import time

from hexacommon.common import network_handler
from hexarpi.programs import remote_control
from hexarpi.utils import gps_util
from hexarpi.utils import movement


class Hexacopter:
    def __init__(self):
        init_time = time.strftime("%y-%m-%d %H:%M:%S")
        logging.info("==== Initiating hexapi " + init_time + " ====")
        # gps_util.start_gps_module()

        self._abort = False
        self._nice_abort = True

        self._nh = network_handler.NetworkHandler(4094)
        self._mov = movement.Movement(50)
        self._gps = gps_util.GPSUtil()

        self._rc_program = remote_control.RcProgram(
            self._mov, self._nh, self._gps)

        self._current_program = self._rc_program

        self._register_callbacks()

        self._nh.start()

    def run(self):
        start_time = time.strftime("%y-%m-%d %H:%M:%S")
        logging.info("==== Starting hexapi " + start_time + " ====")

        while not self._abort:
            self._current_program.run()

        self.abort_flight()

    def abort_flight(self):
        logging.info("MA: Abortign")
        self._nh.stop()
        self._mov.set_yaw(0)
        self._mov.set_pitch(0)
        self._mov.set_roll(0)

        if self._nice_abort:
            logging.info("MA: Slow descent")
            current_altitude = self._mov.altitude_level
            while current_altitude > -100:
                time.sleep(0.3)
                current_altitude -= 1
                self._mov.set_altitude(current_altitude)
        else:
            logging.info("MA: Immediate engine turn off")
            self._mov.set_altitude(-100)

        stop_time = time.strftime("%y-%m-%d %H:%M:%S")
        logging.info("==== Exiting " + stop_time + " ====")

    def set_program_rc(self):
        logging.info("MA: Switching to rc mode")
        old_program = self._current_program
        self._current_program = self._rc_program
        old_program.stop()

    def set_program_gps(self):
        logging.info("MA: Switching to gps mode")
        old_program = self._current_program
        self._current_program = self._gps_program
        old_program.stop()

    def stop(self, *args):
        self._abort = True
        self._current_program.stop()

    def kill(self, *args):
        self._nice_abort = False
        self.stop()

    def _register_callbacks(self):
        logging.info("MA: Registring callbacks")
        # Add all callbacks to the network handler.
        self._nh.register_callback(self.set_program_rc, "START_PROG_RC")
        self._nh.register_callback(self.set_program_gps, "START_PROG_GPS")
        self._nh.register_callback(self.stop, "LAND")
        self._nh.register_callback(self.kill, "KILL")
        self._rc_program.register_callbacks()


def main():
    logging.basicConfig(filename='hexapi_rpi.log', level=logging.DEBUG)
    hexacopter = Hexacopter()
    signal.signal(signal.SIGINT, hexacopter.stop)  # If ctrl + c abort nice.

    hexacopter.run()

if __name__ == '__main__':
    main()
