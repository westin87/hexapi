from time import sleep
import logging

import numpy as np
import signal

from hexachip.hexacommon.common.coordinates import Point2D
from smbus import SMBus


class Position:
    GTPA010_ADDRESS = 0x29
    GTPA010_ID = 0b10101100
    ID = 0x25
    STATUS = 0x00
    UPDATE_RATE = 0x21
    START = 0x23

    LATITUDE_MSB = 0x1
    LATITUDE_AMSB = 0x2
    LATITUDE_ALSB= 0x3
    LATITUDE_LSB = 0x4

    LONGITUDE_MSB = 0x5
    LONGITUDE_AMSB = 0x6
    LONGITUDE_ALSB= 0x7
    LONGITUDE_LSB = 0x8

    ALTITUDE_MSB = 0x17
    ALTITUDE_AMSB = 0x18
    ALTITUDE_ALSB= 0x19
    ALTITUDE_LSB = 0x1A

    def __init__(self):
        self._i2c_bus = SMBus(2)
        self.address = self.GTPA010_ADDRESS

        if self._read_byte(self.ID) == self.GTPA010_ID:
            logging.info("GPS: GTPA010 detected successfully.")
        else:
            logging.info("GPS: No GTPA010 detected")

        self._configure()

    @property
    def latitude(self):
        msb = self._read_byte(self.LATITUDE_MSB)
        amsb = self._read_byte(self.LATITUDE_AMSB)
        alsb = self._read_byte(self.LATITUDE_ALSB)
        lsb = self._read_byte(self.LATITUDE_LSB)

        return _combine_position_bytes(msb, amsb, alsb, lsb)

    @property
    def longitude(self):
        msb = self._read_byte(self.LONGITUDE_MSB)
        amsb = self._read_byte(self.LONGITUDE_AMSB)
        alsb = self._read_byte(self.LONGITUDE_ALSB)
        lsb = self._read_byte(self.LONGITUDE_LSB)

        return _combine_position_bytes(msb, amsb, alsb, lsb)

    @property
    def position(self):
        return Point2D(self.latitude, self.longitude)

    @property
    def altitude(self):
        msb = self._read_byte(self.ALTITUDE_MSB)
        amsb = self._read_byte(self.ALTITUDE_AMSB)
        alsb = self._read_byte(self.ALTITUDE_ALSB)
        lsb = self._read_byte(self.ALTITUDE_LSB)

        return _combine_altitude_bytes(msb, amsb, alsb, lsb)

    @property
    def status(self):
        status_byte = self._read_byte(self.STATUS)
        return GPSStatus(status_byte)

    def __str__(self):
        return "Current position - Lat: {}, Long: {}".\
            format(self.latitude, self.longitude)

    def _write_byte(self, register, value):
        self._i2c_bus.write_byte_data(self.address, register, value)

    def _read_byte(self, register):
        data = np.uint8(self._i2c_bus.read_byte_data(self.address, register))
        return data

    def _configure(self):
        pass


class GPSStatus:
    def __init__(self, status_byte):
        self.new_data = bool(status_byte & 0x1)
        self.rcm_status = bool(status_byte & 0x2)
        self.fix_3d = bool(status_byte & 0x4)
        self.position_fix = bool(status_byte & 0x8)
        self.used_satellites = np.uint32(status_byte >> 4)

    def __str__(self):
        return "Position fix: {}, number of satellites used: {}.".\
            format(self.position_fix, self.used_satellites)


def _combine_position_bytes(msb, amsb, alsb, lsb):
    BYTE_SIZE = 8

    msb = np.uint32(msb)
    amsb = np.uint32(amsb)
    alsb = np.uint32(alsb)
    lsb = np.uint32(lsb)

    value = np.int32(
        msb << (3 * BYTE_SIZE) |
        amsb << (2 * BYTE_SIZE) |
        alsb << (1 * BYTE_SIZE) |
        lsb << (0 * BYTE_SIZE))

    degrees = value // 10**6

    minutes = (value - (degrees * 10**6)) / (10**4)

    decimal_degrees = degrees + (minutes / 60)

    return decimal_degrees


def _combine_altitude_bytes(msb, amsb, alsb, lsb):
    BYTE_SIZE = 8

    msb = np.uint32(msb)
    amsb = np.uint32(amsb)
    alsb = np.uint32(alsb)
    lsb = np.uint32(lsb)

    value = np.int32(
        msb << (3 * BYTE_SIZE) |
        amsb << (2 * BYTE_SIZE) |
        alsb << (1 * BYTE_SIZE) |
        lsb << (0 * BYTE_SIZE))

    return value / (10**2)


class TestPosition:
    def __init__(self):
        self._continue = True
        self._position = Position()
        signal.signal(signal.SIGINT, self._stop)

    def start(self):
        while self._continue:
            sleep(1)
            print("-" * 40)
            print(self._position.status)
            print(self._position)

    def _stop(self, *args):
        self._continue = False


def main():
    test = TestPosition()
    test.start()


if __name__ == '__main__':
    main()