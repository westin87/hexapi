#!/usr/bin/python2

import time
import signal

from network import network_handler
from programs import remote_control
from programs import gps_program
from utils import movement


class Main:
    def __init__(self):
        init_time = time.strftime("%y-%m-%d %H:%M:%S")
        print "==== Initiating hexapi " + init_time + " ===="
        self.__abort = False
        self.__nice_abort = True
        self.__nh = network_handler.NetworkHandler(4092)
        self.__current_program = remote_control.RcProgram()
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
        old_program = self.__current_program
        self.__current_program = remote_control.RcProgram()
        old_program.kill()

    def set_program_gps(self):
        old_program = self.__current_program
        self.__current_program = gps_program.GpsProgram()
        old_program.kill()

    def stop(self, *args):
        self.__abort = True
        self.__current_program.kill()

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
        self.__current_program.register_callbacks(self.__nh)


if __name__ == '__main__':
    main = Main()

    # If ctrl + c abort nice.
    signal.signal(signal.SIGINT, main.stop)

    main.run()
