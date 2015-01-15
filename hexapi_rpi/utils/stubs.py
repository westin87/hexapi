import random
import time
import os
import re

from itertools import cycle


class PWM():
    def __init__(self, data, debug):
        self.freq = -1
        self.channel = -1
        self.startTick = -1
        self.stopTick = -1

        pass

    def setPWMFreq(self, freq):
        print "ST: Frequency set to: " + str(freq)
        self.freq = freq

    def setPWM(self, channel, startTick, stopTick):
        print "ST: PWM set for channel: " + str(channel) +\
            " with start: " + str(startTick) + " and stop: " +\
            str(stopTick)

        self.channel = channel
        self.startTick = startTick
        self.stopTick = stopTick


class gps():

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
        self.fix.latitude = self.fake_lat_iter.next()
        self.fix.longitude = self.fake_long_iter.next()
        self.fix.mode = random.random()
        self.fix.speed = random.random()
        self.fix.time = random.random()
        self.fix.track = random.random()

        time.sleep(0.4)


# GPS related
WATCH_ENABLE = 1


class Fix():
    latitude = 0
    longitude = 0
    altitude = 0
    speed = 0
    altitude = 0
