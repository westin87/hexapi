from __future__ import division
import platform
import threading
from copy import copy

from hexacommon.common.gps_data import GPSData

# Check if on hexcopter or local, if local import stub for testing.
rpi_hosts = ['hexapi', 'raspberrypi']

if platform.node() in rpi_hosts:
    print "GPS: Running on RPI"
    import gps
else:
    print "GPS: Running on local"
    import utils.stubs as gps

GPS_ATTRIBUTES = ['altitude', 'climb', 'epc', 'epd', 'eps', 'ept', 'epv',
                  'epx', 'epy', 'latitude', 'longitude', 'mode', 'speed',
                  'time', 'track']


class GPSPoller(threading.Thread):
    def __init__(self, gps_data):
        threading.Thread.__init__(self)
        self.__gps_data = gps_data
        self.__stop = False
        self.__gpsd = gps.gps(mode=gps.WATCH_ENABLE)

    def run(self):
        while not self.__stop:
            self.__gpsd.next()

            for atter in GPS_ATTRIBUTES:
                self.__gps_data.data[atter] = getattr(self.__gpsd.fix, atter)

    def stop(self):
        self.__stop = True


class GPSUtil():
    class __GPSUtil():
        def __init__(self):
            self.__gps_data = GPSData()
            self.__gps_poller = GPSPoller(self.__gps_data)

            self.__gps_poller.start()

        def get_gps_data(self):
            return copy(self.__gps_data)

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
