from __future__ import division
import platform
import threading

# Check if on hexcopter or local, if local import stub for testing.
rpi_hosts = ['hexapi', 'raspberrypi']

if platform.node() in rpi_hosts:
    print "GPS: Running on RPI"
    import gps
else:
    print "GPS: Running on local"
    from utils.stubs import gps


class GPSData():
    position = (0, 0, 0)
    accuracy = 0
    speed = 0


class GPSPoller(threading.Thread):
    def __init__(self, gps_data):
        threading.Thread.__init__(self)
        self.__gps_data = gps_data
        self.__stop = False
        self.__gpsd = gps(mode=gps.WATCH_ENABLE)

    def run(self):
        while not self.__stop:
            self.__gpsd.next()
            self.__gps_data.position = (self.__gpsd.fix.latitude,
                                        self.__gpsd.fix.longitude,
                                        self.__gpsd.fix.altitude)
            self.__gps_data.speed = self.__gpsd.fix.speed
            self.__gps_data.accuracy = 0

    def stop(self):
        self.__stop = True


class GPSUtil():
    class __GPSUtil():
        def __init__(self):
            self.__gps_data = GPSData()
            self.__gps_poller = GPSPoller(self.__gps_data)

            self.__gps_poller.start()

        def get_position(self):
            return self.__gps_data.position

        def get_accuracy(self):
            return self.__gps_data.accuracy

        def get_speed(self):
            return self.__gps_data.speed

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
