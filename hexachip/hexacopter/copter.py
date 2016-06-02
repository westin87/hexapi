"""Usage: run-hexarpi [options]

Options:
-h, --help           Print this message.
-l, --log-to-stdout  Send log to stdout.

"""

import logging
import signal
import time

import sys
from docopt import docopt

from hexacommon.common.communication import Communication
from hexacopter.programs import remote_control
from hexacopter.utils.movement import Movement
from hexacopter.utils.orientation import Orientation
from hexacopter.utils.position import Position


class Hexacopter:
    def __init__(self):
        init_time = time.strftime("%y-%m-%d %H:%M:%S")
        logging.info("==== Initiating hexacopter " + init_time + " ====")

        self._abort = False
        self._nice_abort = True

        self._communication = Communication(in_port=4094, out_port=4092)
        self._movement = Movement(50)
        self._position = Position()
        self._orientation = Orientation()

        self._rc_program = remote_control.RcProgram(
            self._communication, self._movement, self._position, self._orientation)

        self._current_program = self._rc_program

        self._connect_callbacks()

        self._communication.start()

    def run(self):
        start_time = time.strftime("%y-%m-%d %H:%M:%S")
        logging.info("==== Starting hexapi " + start_time + " ====")

        while not self._abort:
            self._current_program.run()

        self.abort_flight()

    def abort_flight(self):
        logging.info("MA: Abortign")
        self._communication.stop()
        self._movement.set_yaw(0)
        self._movement.set_pitch(0)
        self._movement.set_roll(0)

        if self._nice_abort:
            logging.info("MA: Slow descent")
            current_altitude = self._movement.altitude_level
            while current_altitude > -100:
                time.sleep(0.3)
                current_altitude -= 1
                self._movement.set_altitude(current_altitude)
        else:
            logging.info("MA: Immediate engine turn off")
            self._movement.set_altitude(-100)

        stop_time = time.strftime("%y-%m-%d %H:%M:%S")
        logging.info("==== Exiting " + stop_time + " ====")

    def set_program_rc(self):
        logging.info("MA: Switching to rc mode")
        old_program = self._current_program
        self._current_program = self._rc_program
        old_program.stop()

    def stop(self, *args):
        self._abort = True
        self._current_program.stop()

    def kill(self, *args):
        self._nice_abort = False
        self.stop()

    def _connect_callbacks(self):
        logging.info("MA: Registring callbacks")
        # Add all callbacks to the network handler.
        self._communication.connect_command_callback(self.set_program_rc, "START_PROG_RC")
        self._communication.connect_command_callback(self.stop, "LAND")
        self._communication.connect_command_callback(self.kill, "KILL")


def main():
    arguments = docopt(__doc__)

    if arguments['--log-to-stdout']:
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    else:
        logging.basicConfig(filename='hexacopter.log', level=logging.DEBUG)

    hexacopter = Hexacopter()
    signal.signal(signal.SIGINT, hexacopter.stop)  # If ctrl + c abort nice.

    hexacopter.run()

if __name__ == '__main__':
    main()
