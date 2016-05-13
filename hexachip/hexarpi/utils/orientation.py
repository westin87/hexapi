import logging
from time import sleep

import numpy as np
import signal
from smbus import SMBus

from hexacommon.common.coordinates import Vector2D


class Orientation:
    # --- Constants from BNO055 datasheet ---
    BNO055_ADDRESS = 0x28
    BNO055_WHO_AM_I = 0b10100000  # Device id

    # Control register addresses
    PAGE_ID = 0x07
    UNIT_SEL = 0x3B
    OPR_MODE = 0x3D
    CALIB_STAT = 0x35
    SYS_TRIGGER = 0x3F
    SYS_STATUS = 0x39
    SYS_ERR = 0x3A
    PWR_MODE = 0x3E

    #Registers holding twos-complemented MSB and LSB of euler angle readings
    EUL_DATA_X_LSB = 0x1A
    EUL_DATA_X_MSB = 0x1B
    EUL_DATA_Y_LSB = 0x1C
    EUL_DATA_Y_MSB = 0x1D
    EUL_DATA_Z_LSB = 0x1E
    EUL_DATA_Z_MSB = 0x1F

    def __init__(self):
        self._i2c_bus = SMBus(2)
        self.address = self.BNO055_ADDRESS

        if self._read_byte(0x00) == self.BNO055_WHO_AM_I:
            logging.info("OR: BNO055 detected successfully.")
        else:
            logging.info("OR: No BNO055 detected")

        self._configure()

    @property
    def direction(self):
        direction_angle = self.get_euler_angel()[0]
        direction = Vector2D(x=np.cos(direction_angle), y=np.sin(direction_angle))
        direction /= abs(direction)
        return direction

    def _write_byte(self, register, value):
        self._i2c_bus.write_byte_data(self.address, register, value)

    def _read_byte(self, register):
        data = np.uint8(self._i2c_bus.read_byte_data(self.address, register))
        return data

    def _configure(self):
        logging.info("OR: Configuring BNO055")

        self._write_byte(self.OPR_MODE, 0b00000000)  # Configuration mode
        self._write_byte(self.SYS_TRIGGER, 0b00100000)  # Reset
        sleep(1)
        self._write_byte(self.PWR_MODE, 0b00000000)  # Normal power mode
        self._write_byte(self.PAGE_ID, 0b00000000)  # First page

        self._write_byte(self.SYS_TRIGGER, 0b10000000)  # External oscillator

        self._write_byte(self.UNIT_SEL, 0b00000100)  # Radians
        self._write_byte(self.OPR_MODE, 0b00001100)  # NDOF

    def get_euler_angel(self):
        euler_angel_x = _combine_bytes(
            self._read_byte(self.EUL_DATA_X_MSB),
            self._read_byte(self.EUL_DATA_X_LSB))
        euler_angel_y = _combine_bytes(
            self._read_byte(self.EUL_DATA_Y_MSB),
            self._read_byte(self.EUL_DATA_Y_LSB))
        euler_angel_z = _combine_bytes(
            self._read_byte(self.EUL_DATA_Z_MSB),
            self._read_byte(self.EUL_DATA_Z_LSB))

        return euler_angel_x, euler_angel_y, euler_angel_z

    def get_calibration_status(self):
        return self._read_byte(self.CALIB_STAT)

    def get_system_status(self):
        return self._read_byte(self.SYS_STATUS)

    def get_system_error(self):
        return self._read_byte(self.SYS_ERR)


def _combine_bytes(msb, lsb):
    msb = np.uint16(msb)
    lsb = np.uint16(lsb)

    value = (msb << 8) | lsb

    return np.int16(value) / 900


def radians_to_compass(radians):
    if radians < 1 * np.pi / 6:
        return 'S'
    elif radians < 2 * np.pi / 6:
        return 'SW'
    elif radians < 4 * np.pi / 6:
        return 'W'
    elif radians < 5 * np.pi / 6:
        return 'NW'
    elif radians < 7 * np.pi / 6:
        return 'N'
    elif radians < 8 * np.pi / 6:
        return 'NE'
    elif radians < 10 * np.pi / 6:
        return 'E'
    elif radians < 11 * np.pi / 6:
        return 'SE'
    elif radians <= 12 * np.pi / 6:
        return 'S'


class TestOrientation:
    def __init__(self):
        self._continue = True
        self._orientation = Orientation()
        signal.signal(signal.SIGINT, self._stop)

    def start(self):
        while self._continue:
            sleep(0.1)
            x, y, z = self._orientation.get_euler_angel()
            print(radians_to_compass(x))

    def _stop(self, *args):
        self._continue = False


def main():
    test = TestOrientation()
    test.start()


if __name__ == '__main__':
    main()
