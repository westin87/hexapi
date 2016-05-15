import logging
import math
import time
import smbus


class PWMDriver:
    # Registers/etc.
    PWM_ADDRESS = 0x40
    MODE1 = 0x00
    MODE2 = 0x01
    PRESCALE = 0xFE
    LED0_ON_L = 0x06
    LED0_ON_H = 0x07
    LED0_OFF_L = 0x08
    LED0_OFF_H = 0x09
    ALL_LED_ON_L = 0xFA
    ALL_LED_ON_H = 0xFB
    ALL_LED_OFF_L = 0xFC
    ALL_LED_OFF_H = 0xFD

    # Bits
    SLEEP = 0x10
    ALLCALL = 0x01
    OUTDRV = 0x04

    def __init__(self):
        self._i2c_bus = smbus.SMBus(2)
        self._address = self.PWM_ADDRESS

        self._configure_pwm_driver()

    def _configure_pwm_driver(self):
        self.set_pwm_for_all(0, 0)
        self._write_byte(self.MODE2, self.OUTDRV)
        self._write_byte(self.MODE1, self.ALLCALL)
        time.sleep(0.005)  # wait for oscillator
        mode1 = self._read_byte(self.MODE1)
        mode1 &= ~self.SLEEP  # wake up (reset sleep)
        self._write_byte(self.MODE1, mode1)
        time.sleep(0.005)  # wait for oscillator

    def set_pwm_frequency(self, freq):
        "Sets the PWM frequency"
        pre_scale_value = 25000000.0  # 25MHz
        pre_scale_value /= 4096.0  # 12-bit
        pre_scale_value /= float(freq)
        pre_scale_value -= 1.0

        logging.info("Setting PWM frequency to {} Hz".format(freq))

        pre_scale = math.floor(pre_scale_value + 0.5)

        old_mode = self._read_byte(self.MODE1)
        new_mode = (old_mode & 0x7F) | 0x10  # sleep
        self._write_byte(self.MODE1, new_mode)  # go to sleep
        self._write_byte(self.PRESCALE, int(math.floor(pre_scale)))
        self._write_byte(self.MODE1, old_mode)
        time.sleep(0.005)
        self._write_byte(self.MODE1, old_mode | 0x80)

    def set_pwm(self, channel, on, off):
        "Sets a single PWM channel"
        self._write_byte(self.LED0_ON_L + 4 * channel, on & 0xFF)
        self._write_byte(self.LED0_ON_H + 4 * channel, on >> 8)
        self._write_byte(self.LED0_OFF_L + 4 * channel, off & 0xFF)
        self._write_byte(self.LED0_OFF_H + 4 * channel, off >> 8)

    def set_pwm_for_all(self, on, off):
        "Sets a all PWM channels"
        self._write_byte(self.ALL_LED_ON_L, on & 0xFF)
        self._write_byte(self.ALL_LED_ON_H, on >> 8)
        self._write_byte(self.ALL_LED_OFF_L, off & 0xFF)
        self._write_byte(self.ALL_LED_OFF_H, off >> 8)

    def _write_byte(self, register, value):
        self._i2c_bus.write_byte_data(self._address, register, value)

    def _read_byte(self, register):
        return self._i2c_bus.read_byte_data(self._address, register)