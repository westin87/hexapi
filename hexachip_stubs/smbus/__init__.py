import logging
import random


class SMBus:
    def __init__(self, interface):
        pass

    def read_byte_data(self, address, register):
        return random.randrange(0, 256)

    def write_byte_data(self, address, register, value):
        # logging.info("SM: Writing byte {} to register {} on address {}"
        #       .format(value, register, address))
        pass
