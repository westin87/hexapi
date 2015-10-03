from __future__ import division
import platform
from hexacommon.common import singleton

# Check if on hexcopter or local, if local import stub for testing.
rpi_hosts = ['hexapi', 'raspberrypi']

if platform.node() in rpi_hosts:
    print "MV: Running on RPI"
    import hexarpi.utils.Adafruit_PWM_Servo_Driver as ada
else:
    print "MV: Running on local"
    import hexarpi.utils.stubs as ada


class Movement:
    def __init__(self, freq):
        # Initialise the PWM device using the default address

        self._pwm = ada.PWM(0x40, debug=False)

        self._pwm.setPWMFreq(freq)
        self._tick_length = (1/freq)/4096  # Length in s of a tick

        self._pitch_channel = 1
        self._roll_channel = 0
        self._yaw_channel = 3
        self._altitude_channel = 2
        self._mode_channel = 4

        self.altitude_level = 0

        self.set_altitude(-100)
        self.set_yaw(0)
        self.set_pitch(0)
        self.set_roll(0)
        self.set_mode(20)

    def set_servo_pulse(self, channel, pulse):
        """Sets to puls width on selected PWM channel.

        :param channel: channel (0-15)
        :param pulse: pulse width in ms
        """
        puls_in_s = pulse/1000  # Convert to from ms to s.
        ticks = puls_in_s/self._tick_length
        self._pwm.setPWM(channel, 0, int(ticks))

    def _check_range(self, value_range, description):
        if not((-100 <= value_range) and (value_range <= 100)):
            print("MO: Invalid speed set for " + description)

    def set_pitch(self, speed):
        self._check_range(speed, "pitch")
        pulse = 1.5 + (speed/200)
        self.set_servo_pulse(self._pitch_channel, pulse)

    def set_roll(self, speed):
        self._check_range(speed, "roll")
        pulse = 1.5 + (speed/200)
        self.set_servo_pulse(self._roll_channel, pulse)

    def set_yaw(self, speed):
        self._check_range(speed, "yaw")
        pulse = 1.5 + (speed/200)
        self.set_servo_pulse(self._yaw_channel, pulse)

    def set_altitude(self, level):
        self._check_range(level, "altitude")
        self.altitude_level = level
        pulse = 1.5 + (level/200)
        self.set_servo_pulse(self._altitude_channel, pulse)

    def set_mode(self, level):
        pulse = 1.5 + (level/200)
        self.set_servo_pulse(self._mode_channel, pulse)
