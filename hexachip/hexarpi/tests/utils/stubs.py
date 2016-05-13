import logging

import random
import time
import os
import re

from itertools import cycle


class gps:
    def __init__(self, mode):
        self.fix = Fix()
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "fake_data.dat")) as fo:
            fake_gps_data = fo.readlines()

        fake_lat = []
        fake_long = []
        for fake_data_point in fake_gps_data:
            match = re.search("latitude: \d*\.\d*", fake_data_point)
            fake_lat.append(float(match.group().split(": ")[1]))

            match = re.search("longitude: \d*\.\d*", fake_data_point)
            fake_long.append(float(match.group().split(": ")[1]))

        self.fake_lat_iter = cycle(fake_lat)
        self.fake_long_iter = cycle(fake_long)

    def next(self):
        self.fix.altitude = random.random()
        self.fix.climb = random.random()
        self.fix.epc = random.random()
        self.fix.epd = random.random()
        self.fix.eps = random.random()
        self.fix.ept = random.random()
        self.fix.epv = random.random()
        self.fix.epx = random.random()
        self.fix.epy = random.random()
        self.fix.latitude = next(self.fake_lat_iter)
        self.fix.longitude = next(self.fake_long_iter)
        self.fix.mode = random.random()
        self.fix.speed = random.random()
        self.fix.time = random.random()
        self.fix.track = random.random()

        time.sleep(0.4)


# GPS related
WATCH_ENABLE = 1


class Fix:
    def __init__(self):
        self.latitude = 0
        self.longitude = 0
        self.altitude = 0
        self.speed = 0
        self.altitude = 0


class SMBus:
    def __init__(self, interface):
        pass

    def read_byte_data(self, address, register):
        return random.randrange(0, 256)

    def write_byte_data(self, address, register, value):
        logging.info("SM: Writing byte {} to register {} on address {}"
              .format(value, register, address))