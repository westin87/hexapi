from __future__ import division
import platform

# Check if on hexcopter or local, if local import stub for testing.
rpi_hosts = ['hexapi', 'raspberrypi']

if platform.node() in rpi_hosts:
    print "MV: Running on RPI"
    from hexarpi.smbus import SMBus
else:
    print "MV: Running on local"
    from hexarpi.utils.stubs import SMBus


# --- Constants from LSM303D datasheet ---
LSM303D = 0x1d
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

#Registers holding twos-complemented MSB and LSB of magnetometer readings
LSM303D_ACC_X_LSB = 0x28
LSM303D_ACC_X_MSB = 0x29
LSM303D_ACC_Y_LSB = 0x2A
LSM303D_ACC_Y_MSB = 0x2B
LSM303D_ACC_Z_LSB = 0x2C
LSM303D_ACC_Z_MSB = 0x2D

#Registers holding 12-bit right justified, twos-complemented temperature data
LSM303D_TEMP_MSB = 0x05
LSM303D_TEMP_LSB = 0x06

# --- Constants from L3GD20H datasheet ---
L3GD20H = 0x35
L3GD20H_WHO_AM_I = 0b11010111 # Device id

L3GD20H_CTRL_1 = 0x20  # General settings
L3GD20H_CTRL_2 = 0x21  # Filter configuration
L3GD20H_CTRL_3 = 0x22  # Interrupts
L3GD20H_CTRL_4 = 0x23  # Data format and self-test
L3GD20H_CTRL_5 = 0x24  # FIFO and other settings

L3GD20H_COM_X_LSB = 0x28
L3GD20H_COM_X_MSB = 0x29
L3GD20H_COM_Y_LSB = 0x2A
L3GD20H_COM_Y_MSB = 0x2B
L3GD20H_COM_Z_LSB = 0x2C
L3GD20H_COM_Z_MSB = 0x2D

class Orientation():
    class __Orientation():
        def __init__(self):
            self.__i2c_bus = SMBus(1)

            if self.__i2c_bus.read_byte_data(LSM303D, 0x0f) == LSM303D_WHO_AM_I:
                print "LSM303D detected successfully."
            else:
                print "No LSM303D detected"

            if self.__i2c_bus.read_byte_data(L3GD20H, 0x0f) == L3GD20H_WHO_AM_I:
                print "LSM303D detected successfully."
            else:
                print "No LSM303D detected"

            self.__configure_LSM303D()
            self.__configure_L3GD20H()

        def __write_byte(self, address, register, value):
            self.__i2c_bus.write_byte_data(address, register, value)

        def __read_byte(self, address, register):
            self.__i2c_bus.read_byte_data(address, register)

        def __configure_LSM303D(self):
            self.__write_byte(LSM303D, LSM303D_CTRL_1, 0b01010111)  # enable accelerometer, 50 hz sampling
            self.__write_byte(LSM303D, LSM303D_CTRL_2, 0b00000000)  # set +/- 2g full scale
            self.__write_byte(LSM303D, LSM303D_CTRL_5, 0b01100100)  # high resolution mode, thermometer off, 6.25hz ODR
            self.__write_byte(LSM303D, LSM303D_CTRL_6, 0b00100000)  # set +/- 4 gauss full scale
            self.__write_byte(LSM303D, LSM303D_CTRL_7, 0b00000000)  # get magnetometer out of low power mode

        def __configure_L3GD20H(self):
            self.__write_byte(L3GD20H, L3GD20H_CTRL_1, 0b10001111)  # enable gyroscope, set 50 hz data rate
            self.__write_byte(L3GD20H, L3GD20H_CTRL_2, 0b00000000)  # set normal hp filter, set 4 hz cut off
            self.__write_byte(L3GD20H, L3GD20H_CTRL_4, 0b00000000)  # continues updates
            self.__write_byte(L3GD20H, L3GD20H_CTRL_5, 0b00000000)  # no FIFO, no HP filter

        def __combine_two_comp(self, msb, lsb):
            value = (msb << 8) | lsb

            if value & 0x8000:
                value = -((~value & 0xFFFF) + 0x1)

            return value

        def get_acceleration(self):
            acceleration_x = self.__combine_two_comp(
                self.__read_byte(LSM303D, LSM303D_ACC_X_MSB),
                self.__read_byte(LSM303D, LSM303D_ACC_X_LSB))
            acceleration_y = self.__combine_two_comp(
                self.__read_byte(LSM303D, LSM303D_ACC_Y_MSB),
                self.__read_byte(LSM303D, LSM303D_ACC_Y_LSB))
            acceleration_z = self.__combine_two_comp(
                self.__read_byte(LSM303D, LSM303D_ACC_Z_MSB),
                self.__read_byte(LSM303D, LSM303D_ACC_Z_LSB))

            return acceleration_x, acceleration_y, acceleration_z

        def get_magnetic_field(self):
            magnetic_x = self.__combine_two_comp(
                self.__read_byte(LSM303D, LSM303D_MAG_X_MSB),
                self.__read_byte(LSM303D, LSM303D_MAG_X_LSB))
            magnetic_y = self.__combine_two_comp(
                self.__read_byte(LSM303D, LSM303D_MAG_Y_MSB),
                self.__read_byte(LSM303D, LSM303D_MAG_Y_LSB))
            magnetic_z = self.__combine_two_comp(
                self.__read_byte(LSM303D, LSM303D_MAG_Z_MSB),
                self.__read_byte(LSM303D, LSM303D_MAG_Z_LSB))

            return magnetic_x, magnetic_y, magnetic_z

        def get_angular_rate(self):
            angular_rate_x = self.__combine_two_comp(
                self.__read_byte(L3GD20H, L3GD20H_COM_X_MSB),
                self.__read_byte(L3GD20H, L3GD20H_COM_X_LSB))
            angular_rate_y = self.__combine_two_comp(
                self.__read_byte(L3GD20H, L3GD20H_COM_Y_MSB),
                self.__read_byte(L3GD20H, L3GD20H_COM_Y_LSB))
            angular_rate_z = self.__combine_two_comp(
                self.__read_byte(L3GD20H, L3GD20H_COM_Z_MSB),
                self.__read_byte(L3GD20H, L3GD20H_COM_Z_LSB))

            return angular_rate_x, angular_rate_y, angular_rate_z

    __instance = None

    def __init__(self):
        if not Orientation.__instance:
            Orientation.__instance = Orientation.__Orientation()

    def __getattr__(self, value):
        return getattr(self.__instance, value)

    def __setattr__(self, attr, value):
        return setattr(self.__instance, attr, value)
