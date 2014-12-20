import random
import time


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
        self.fix.latitude = random.random()
        self.fix.longitude = random.random()
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
