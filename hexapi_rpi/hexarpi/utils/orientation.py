from __future__ import division
import platform

# Check if on hexcopter or local, if local import stub for testing.
rpi_hosts = ['hexapi', 'raspberrypi']

if platform.node() in rpi_hosts:
    print "OR: Running on RPI"
    from smbus import SMBus
else:
    print "OR: Running on local"
    from hexarpi.utils.stubs import SMBus


class Orientation:
    # --- Constants from BNO055 datasheet ---
    BNO055_ADDRESS = 0x28
    BNO055_WHO_AM_I = 0b10100000  # Device id

    # Control register addresses

    #Registers holding twos-complemented MSB and LSB of euler angle readings
    EUL_DATA_X_LSB = 0x1A
    EUL_DATA_X_MSB = 0x1B
    EUL_DATA_Y_LSB = 0x1C
    EUL_DATA_Y_MSB = 0x1D
    EUL_DATA_Z_LSB = 0x1E
    EUL_DATA_Z_MSB = 0x1F

    def __init__(self):
        self._i2c_bus = SMBus(1)
        self.address = self.BNO055_ADDRESS

        if self._read_byte(0x00) == self.BNO055_WHO_AM_I:
            print "OR: BNO055 detected successfully."
        else:
            print "OR: No BNO055 detected"

        self._configure()

    def _write_byte(self, register, value):
        self._i2c_bus.write_byte_data(self.address, register, value)

    def _read_byte(self, register):
        return self._i2c_bus.read_byte_data(self.address, register)

    def _configure(self):
        print "OR: Configuring BNO055"
        self._write_byte(self.BNO055_CTRL_1, 0b01010111)  # enable accelerometer, 50 hz sampling
        self._write_byte(self.BNO055_CTRL_2, 0b00000000)  # set +/- 2g full scale
        self._write_byte(self.BNO055_CTRL_5, 0b01100100)  # high resolution mode, thermometer off, 6.25hz ODR
        self._write_byte(self.BNO055_CTRL_6, 0b00100000)  # set +/- 4 gauss full scale
        self._write_byte(self.BNO055_CTRL_7, 0b00000000)  # get magnetometer out of low power mode

    def get_acceleration(self):
        acceleration_x = _combine_two_comp(
            self._read_byte(self.BNO055_ACC_X_MSB),
            self._read_byte(self.BNO055_ACC_X_LSB))
        acceleration_y = _combine_two_comp(
            self._read_byte(self.BNO055_ACC_Y_MSB),
            self._read_byte(self.BNO055_ACC_Y_LSB))
        acceleration_z = _combine_two_comp(
            self._read_byte(self.BNO055_ACC_Z_MSB),
            self._read_byte(self.BNO055_ACC_Z_LSB))

        return acceleration_x, acceleration_y, acceleration_z


def _combine_two_comp(msb, lsb):
    value = (msb << 8) | lsb

    if value & 0x8000:
        value = -((~value & 0xFFFF) + 0x1)

    return value
