from __future__ import division

from time import sleep

import numpy as np
import platform

# Check if on hexcopter or local, if local import stub for testing.
rpi_hosts = ['hexapi', 'raspberrypi']

if platform.node() in rpi_hosts:
    print "OR: Running on RPI"
    from smbus import SMBus
else:
    print "OR: Running on local"
    from hexarpi.utils.stubs import SMBus


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
        self._i2c_bus = SMBus(1)
        self.address = self.BNO055_ADDRESS

        if self._read_byte(0x00) == self.BNO055_WHO_AM_I:
            print "OR: BNO055 detected successfully."
        else:
            print "OR: No BNO055 detected"

        self._configure()

    def _write_byte(self, register, value):
        self._i2c_bus.write_byte_data(self.address, register, value)

    def _read_byte(self, register):
        return self._i2c_bus.read_byte_data(self.address, register)

    def _configure(self):
        print "OR: Configuring BNO055"

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
