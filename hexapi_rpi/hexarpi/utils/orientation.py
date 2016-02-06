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

    def __init__(self):
        self.lsm303d = LSM303D()
        self.l3gd20h = L3GD20H()

    def get_acceleration(self):
        return self.lsm303d.get_acceleration()

    def get_magnetic_field(self):
        return self.lsm303d.get_magnetic_field()

    def get_angular_rate(self):
        return self.l3gd20h.get_angular_rate()


class LSM303D:
    # --- Constants from LSM303D datasheet ---
    LSM303D_ADDRESS = 0x1D
    LSM303D_WHO_AM_I = 0b01001001  # Device id

    # Control register addresses
    LSM303D_CTRL_0 = 0x1F  #General settings
    LSM303D_CTRL_1 = 0x20  #Turns on accelerometer and configures data rate
    LSM303D_CTRL_2 = 0x21  #Self test accelerometer, anti-aliasing accel filter
    LSM303D_CTRL_3 = 0x22  #Interrupts
    LSM303D_CTRL_4 = 0x23  #Interrupts
    LSM303D_CTRL_5 = 0x24  #Turns on temperature sensor
    LSM303D_CTRL_6 = 0x25  #Magnetic resolution selection, data rate config
    LSM303D_CTRL_7 = 0x26  #Turns on magnetometer and adjusts mode

    #Registers holding twos-complemented MSB and LSB of magnetometer readings
    LSM303D_MAG_X_LSB = 0x08
    LSM303D_MAG_X_MSB = 0x09
    LSM303D_MAG_Y_LSB = 0x0A
    LSM303D_MAG_Y_MSB = 0x0B
    LSM303D_MAG_Z_LSB = 0x0C
    LSM303D_MAG_Z_MSB = 0x0D

    #Registers holding twos-complemented MSB and LSB of accelerometer readings
    LSM303D_ACC_X_LSB = 0x28
    LSM303D_ACC_X_MSB = 0x29
    LSM303D_ACC_Y_LSB = 0x2A
    LSM303D_ACC_Y_MSB = 0x2B
    LSM303D_ACC_Z_LSB = 0x2C
    LSM303D_ACC_Z_MSB = 0x2D

    #Registers holding 12-bit right justified, twos-complemented temperature data
    LSM303D_TEMP_MSB = 0x05
    LSM303D_TEMP_LSB = 0x06

    def __init__(self):
        self._i2c_bus = SMBus(1)
        self.address = self.LSM303D_ADDRESS

        if self._read_byte(0x0F) == self.LSM303D_WHO_AM_I:
            print "OR: LSM303D detected successfully."
        else:
            print "OR: No LSM303D detected"

        self._configure_LSM303D()

    def _write_byte(self, register, value):
        self._i2c_bus.write_byte_data(self.address, register, value)

    def _read_byte(self, register):
        return self._i2c_bus.read_byte_data(self.address, register)

    def _configure_LSM303D(self):
        print "OR: Configuring LSM303D"
        self._write_byte(self.LSM303D_CTRL_1, 0b01010111)  # enable accelerometer, 50 hz sampling
        self._write_byte(self.LSM303D_CTRL_2, 0b00000000)  # set +/- 2g full scale
        self._write_byte(self.LSM303D_CTRL_5, 0b01100100)  # high resolution mode, thermometer off, 6.25hz ODR
        self._write_byte(self.LSM303D_CTRL_6, 0b00100000)  # set +/- 4 gauss full scale
        self._write_byte(self.LSM303D_CTRL_7, 0b00000000)  # get magnetometer out of low power mode

    def get_acceleration(self):
        acceleration_x = _combine_two_comp(
            self._read_byte(self.LSM303D_ACC_X_MSB),
            self._read_byte(self.LSM303D_ACC_X_LSB))
        acceleration_y = _combine_two_comp(
            self._read_byte(self.LSM303D_ACC_Y_MSB),
            self._read_byte(self.LSM303D_ACC_Y_LSB))
        acceleration_z = _combine_two_comp(
            self._read_byte(self.LSM303D_ACC_Z_MSB),
            self._read_byte(self.LSM303D_ACC_Z_LSB))

        return acceleration_x, acceleration_y, acceleration_z

    def get_magnetic_field(self):
        magnetic_x = _combine_two_comp(
            self._read_byte(self.LSM303D_MAG_X_MSB),
            self._read_byte(self.LSM303D_MAG_X_LSB))
        magnetic_y = _combine_two_comp(
            self._read_byte(self.LSM303D_MAG_Y_MSB),
            self._read_byte(self.LSM303D_MAG_Y_LSB))
        magnetic_z = _combine_two_comp(
            self._read_byte(self.LSM303D_MAG_Z_MSB),
            self._read_byte(self.LSM303D_MAG_Z_LSB))

        return magnetic_x, magnetic_y, magnetic_z


class L3GD20H():
    # --- Constants from L3GD20H datasheet ---
    L3GD20H_ADDRESS = 0x6B
    L3GD20H_WHO_AM_I = 0b11010111  # Device id

    # Control register addresses
    L3GD20H_CTRL_1 = 0x20  # General settings
    L3GD20H_CTRL_2 = 0x21  # Filter configuration
    L3GD20H_CTRL_3 = 0x22  # Interrupts
    L3GD20H_CTRL_4 = 0x23  # Data format and self-test
    L3GD20H_CTRL_5 = 0x24  # FIFO and other settings

    #Registers holding twos-complemented MSB and LSB of gyroscope readings
    L3GD20H_COM_X_LSB = 0x28
    L3GD20H_COM_X_MSB = 0x29
    L3GD20H_COM_Y_LSB = 0x2A
    L3GD20H_COM_Y_MSB = 0x2B
    L3GD20H_COM_Z_LSB = 0x2C
    L3GD20H_COM_Z_MSB = 0x2D

    def __init__(self):
        self._i2c_bus = SMBus(1)
        self.address = self.L3GD20H_ADDRESS

        if self._read_byte(0x0F) == self.L3GD20H_WHO_AM_I:
            print "OR: L3GD20H detected successfully."
        else:
            print "OR: No L3GD20H detected"

        self._configure_L3GD20H()

    def _write_byte(self, register, value):
        self._i2c_bus.write_byte_data(self.address, register, value)

    def _read_byte(self, register):
        return self._i2c_bus.read_byte_data(self.address, register)

    def _configure_L3GD20H(self):
        print "OR: Configuring L3GD20H"
        self._write_byte(self.L3GD20H_CTRL_1, 0b10001111)  # enable gyroscope, set 50 hz data rate
        self._write_byte(self.L3GD20H_CTRL_2, 0b00000000)  # set normal hp filter, set 4 hz cut off
        self._write_byte(self.L3GD20H_CTRL_4, 0b00000000)  # continues updates
        self._write_byte(self.L3GD20H_CTRL_5, 0b00000000)  # no FIFO, no HP filter

    def get_angular_rate(self):
        angular_rate_x = _combine_two_comp(
            self._read_byte(self.L3GD20H_COM_X_MSB),
            self._read_byte(self.L3GD20H_COM_X_LSB))
        angular_rate_y = _combine_two_comp(
            self._read_byte(self.L3GD20H_COM_Y_MSB),
            self._read_byte(self.L3GD20H_COM_Y_LSB))
        angular_rate_z = _combine_two_comp(
            self._read_byte(self.L3GD20H_COM_Z_MSB),
            self._read_byte(self.L3GD20H_COM_Z_LSB))

        return angular_rate_x, angular_rate_y, angular_rate_z


def _combine_two_comp(msb, lsb):
    value = (msb << 8) | lsb

    if value & 0x8000:
        value = -((~value & 0xFFFF) + 0x1)

    return value
