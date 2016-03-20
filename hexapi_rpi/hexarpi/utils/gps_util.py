import logging

import platform
import subprocess
import threading
from copy import copy
from time import sleep

from hexacommon.common.gps_data import GPSData

# Check if on hexacopter or local, if local import stub for testing.
rpi_hosts = ['hexapi', 'raspberrypi', 'chip']

if platform.node() in rpi_hosts:
    logging.info("GPS: Running on hexacopter host")
    import gps
else:
    logging.info("GPS: Running on local")
    import hexarpi.tests.utils.stubs as gps

GPS_ATTRIBUTES = ['altitude', 'climb', 'epc', 'epd', 'eps', 'ept', 'epv',
                  'epx', 'epy', 'latitude', 'longitude', 'mode', 'speed',
                  'time', 'track']


class GPSPoller(threading.Thread):
    def __init__(self, gps_data):
        threading.Thread.__init__(self)
        self._gps_data = gps_data
        self._stop_thread = False
        self._gpsd = gps.gps(mode=gps.WATCH_ENABLE)

    def run(self):
        while not self._stop_thread:
            self._gpsd.next()

            for attribute in GPS_ATTRIBUTES:
                self._gps_data.data[attribute] = getattr(self._gpsd.fix, attribute)

    def stop(self):
        self._stop_thread = True


class GPSUtil:
    def __init__(self):
        self.__gps_data = GPSData()
        self.__gps_poller = GPSPoller(self.__gps_data)

        self.__gps_poller.start()

    def get_gps_data(self):
        return copy(self.__gps_data)

    def kill(self):
        self.__gps_poller.stop()


def start_gps_module():
    try:
        subprocess.call(["sudo", "gpsd", "/dev/ttyAMA0"])
        sleep(4)
    except Exception:
        pass
