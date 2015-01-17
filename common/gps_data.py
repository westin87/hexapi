import re

GPS_ATTRIBUTES = ['altitude', 'climb', 'epc', 'epd', 'eps', 'ept', 'epv',
                  'epx', 'epy', 'latitude', 'longitude', 'mode', 'speed',
                  'time', 'track']

class GPSData():
    def __init__(self, data_str=None):
        self.data = dict()

        for atter in GPS_ATTRIBUTES:
            self.data[atter] = 0.0

        if data_str:
            for atter in GPS_ATTRIBUTES:
                match = re.search("{}: \d*\.\d*".format(atter), data_str)
                if match:
                    self.data[atter] = float(match.group().split(": ")[1])

    def __str__(self):
        return ", ".join(["{}: {}".format(key, value)
                          for key, value in self.data.items()])