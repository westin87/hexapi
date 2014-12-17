from __future__ import division
import platform
import threading
import time
import os
from copy import copy


# Check if on hexcopter or local, if local import stub for testing.
rpi_hosts = ['hexapi', 'raspberrypi']

if platform.node() in rpi_hosts:
    print "GPS: Running on RPI"
    from gps import gps
else:
    print "GPS: Running on local"
    from utils.stubs import gps

GPS_ATTRIBUTES = ['altitude', 'climb', 'epc', 'epd', 'eps', 'ept', 'epv',
                  'epx', 'epy', 'latitude', 'longitude', 'mode', 'speed',
                  'time', 'track']


class GPSData():
    def __init__(self):
        self.data = dict()
        for atter in GPS_ATTRIBUTES:
            self.data[atter] = 0.0

    def __str__(self):
        return ", ".join(["{}: {:.16f}".format(key, value)
                          for key, value in self.data.items()])


class GPSPoller(threading.Thread):
    def __init__(self, gps_data):
        threading.Thread.__init__(self)
        self.__gps_data = gps_data
        self.__stop = False
        self.__gpsd = gps(mode=gps.WATCH_ENABLE)
        self.__datafile = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), "gps_data.log")
        print(__file__)
        with open(self.__datafile, mode='a+') as f:
            f.write("GPS collection started: {}\n"
                    .format(time.strftime("%y/%m/%d %H:%M:%S")))

    def run(self):
        while not self.__stop:
            self.__gpsd.next()

            for atter in GPS_ATTRIBUTES:
                self.__gps_data.data[atter] = getattr(self.__gpsd.fix, atter)

            with open(self.__datafile, 'a+') as f:
                f.write(str(self.__gps_data)+"\n")

        with open(self.__datafile, 'a+') as f:
            f.write("\n")

    def stop(self):
        self.__stop = True


class GPSUtil():
    class __GPSUtil():
        def __init__(self):
            self.__gps_data = GPSData()
            self.__gps_poller = GPSPoller(self.__gps_data)

            self.__gps_poller.start()

        def get_gps_data(self):
            return copy(self.__gps_data.data)

        def kill(self):
            self.__gps_poller.stop()

    __instance = None

    def __init__(self):
        if not GPSUtil.__instance:
            GPSUtil.__instance = GPSUtil.__GPSUtil()

    def __getattr__(self, value):
        return getattr(self.__instance, value)

    def __setattr__(self, attr, value):
        return setattr(self.__instance, attr, value)
