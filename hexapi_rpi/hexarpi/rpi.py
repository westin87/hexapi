#!/usr/bin/python2

import time
import signal
import sys

sys.dont_write_bytecode = True

from hexarpi.network import network_handler
from hexarpi.programs import remote_control
from hexarpi.programs import gps_program
from hexarpi.utils import movement
from hexarpi.utils import gps_util


class Main:
    def __init__(self):
        init_time = time.strftime("%y-%m-%d %H:%M:%S")
        print "==== Initiating hexapi " + init_time + " ===="
        self.__abort = False
        self.__nice_abort = True
        self.__nh = network_handler.NetworkHandler(4092)
        self.__rc_program = remote_control.RcProgram(self.__nh)
        self.__gps_program = gps_program.GpsProgram()
        self.__current_program = self.__rc_program
        self.__register_callbacks()
        self.__nh.start()

    def run(self):
        start_time = time.strftime("%y-%m-%d %H:%M:%S")
        print "==== Starting hexapi " + start_time + " ===="
        while not self.__abort:
            self.__current_program.run()
        self.abort_flight()

    def abort_flight(self):
        print "MA: Abortign"
        m = movement.Movement(50)
        self.__nh.stop()
        m.set_yaw(0)
        m.set_pitch(0)
        m.set_roll(0)
        if self.__nice_abort:
            print "MA: Slow descent"
            current_altitude = m.altitude_level
            while current_altitude > -100:
                time.sleep(0.3)
                current_altitude -= 1
                m.set_altitude(current_altitude)
        else:
            print "MA: Immediate engine turn off"
            m.set_altitude(-100)

        stop_time = time.strftime("%y-%m-%d %H:%M:%S")
        print "==== Exiting " + stop_time + " ====\n"

    def set_program_rc(self):
        print "MA: Switching to rc mode"
        old_program = self.__current_program
        self.__current_program = self.__rc_program
        old_program.stop()

    def set_program_gps(self):
        print "MA: Switching to gps mode"
        old_program = self.__current_program
        self.__current_program = self.__gps_program
        old_program.stop()

    def stop(self, *args):
        gps = gps_util.GPSUtil()
        self.__abort = True
        self.__current_program.stop()

    def kill(self, *args):
        self.__nice_abort = False
        self.stop()

    def __register_callbacks(self):
        print "MA: Registring callbacks"
        # Add all callbacks to the network handler.
        self.__nh.register_callback(self.set_program_rc, "START_PROG_RC")
        self.__nh.register_callback(self.set_program_gps, "START_PROG_GPS")
        self.__nh.register_callback(self.stop, "LAND")
        self.__nh.register_callback(self.kill, "KILL")
        self.__rc_program.register_callbacks()
        self.__gps_program.register_callbacks(self.__nh)


def main():
    main = Main()

    # If ctrl + c abort nice.
    signal.signal(signal.SIGINT, main.stop)

    main.run()

if __name__ == '__main__':
    main()
