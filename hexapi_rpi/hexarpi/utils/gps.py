import logging
import numpy as np

import platform

real_hosts = ['hexapi', 'raspberrypi', 'chip']

if platform.node() in real_hosts:
    logging.info("OR: Running on hexacopter host")
    from smbus import SMBus
else:
    logging.info("OR: Running on localhost")
    from hexarpi.tests.utils.stubs import SMBus


class GPS:
    GTPA010_ADDRESS = 0x00
    STATUS = 0x00

    def __init__(self):
        self._i2c_bus = SMBus(1)
        self.address = self.BNO055_ADDRESS

        if self._read_byte(0x00) == self.BNO055_WHO_AM_I:
            logging.info("GPS: GTPA010 detected successfully.")
        else:
            logging.info("GPS: No GTPA010 detected")

        self._configure()

    def _write_byte(self, register, value):
        self._i2c_bus.write_byte_data(self.address, register, value)

    def _read_byte(self, register):
        data = np.uint8(self._i2c_bus.read_byte_data(self.address, register))
        return data

    def _configure(self):
        self._write_byte()


def _combine_bytes(msb, amsb, alsb, lsb):
    BYTE_SIZE = 8

    msb = np.uint32(msb)
    amsb = np.uint32(amsb)
    alsb = np.uint32(alsb)
    lsb = np.uint32(lsb)

    value = (msb << (3 * BYTE_SIZE) |
             amsb << (2 * BYTE_SIZE) |
             alsb << (1 * BYTE_SIZE) |
             lsb << (0 * BYTE_SIZE))

    return np.int32(value) / (10**4)