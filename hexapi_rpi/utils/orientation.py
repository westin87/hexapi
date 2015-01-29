from __future__ import division
import platform

# Check if on hexcopter or local, if local import stub for testing.
rpi_hosts = ['hexapi', 'raspberrypi']

if platform.node() in rpi_hosts:
    print "MV: Running on RPI"
    from smbus import SMBus
    import utils.Adafruit_PWM_Servo_Driver as ada
else:
    print "MV: Running on local"
    from utils.stubs import SMBus

LSM = 0x1d

LSM_WHOAMI = 0b1001001 #Device self-id

#Control register addresses -- from LSM303D datasheet
CTRL_0 = 0x1F #General settings
CTRL_1 = 0x20 #Turns on accelerometer and configures data rate
CTRL_2 = 0x21 #Self test accelerometer, anti-aliasing accel filter
CTRL_3 = 0x22 #Interrupts
CTRL_4 = 0x23 #Interrupts
CTRL_5 = 0x24 #Turns on temperature sensor
CTRL_6 = 0x25 #Magnetic resolution selection, data rate config
CTRL_7 = 0x26 #Turns on magnetometer and adjusts mode

#Registers holding twos-complemented MSB and LSB of magnetometer readings -- from LSM303D datasheet
MAG_X_LSB = 0x08 # x
MAG_X_MSB = 0x09
MAG_Y_LSB = 0x0A # y
MAG_Y_MSB = 0x0B
MAG_Z_LSB = 0x0C # z
MAG_Z_MSB = 0x0D

#Registers holding twos-complemented MSB and LSB of magnetometer readings -- from LSM303D datasheet
ACC_X_LSB = 0x28 # x
ACC_X_MSB = 0x29
ACC_Y_LSB = 0x2A # y
ACC_Y_MSB = 0x2B
ACC_Z_LSB = 0x2C # z
ACC_Z_MSB = 0x2D

#Registers holding 12-bit right justified, twos-complemented temperature data -- from LSM303D datasheet
TEMP_MSB = 0x05
TEMP_LSB = 0x06


class Orientation():
    class __Orientation():
        def __init__(self):
            self.__i2c_bus = SMBus(1)

            if self.__i2c_bus.read_byte_data(LSM, 0x0f) == LSM_WHOAMI:
                print "LSM303D detected successfully."
            else:
                print "No LSM303D detected"

            self.__i2c_bus.write_byte_data(LSM, CTRL_1, 0b1010111) # enable accelerometer, 50 hz sampling
            self.__i2c_bus.write_byte_data(LSM, CTRL_2, 0x00) #set +/- 2g full scale
            self.__i2c_bus.write_byte_data(LSM, CTRL_5, 0b01100100) #high resolution mode, thermometer off, 6.25hz ODR
            self.__i2c_bus.write_byte_data(LSM, CTRL_6, 0b00100000) # set +/- 4 gauss full scale
            self.__i2c_bus.write_byte_data(LSM, CTRL_7, 0x00) #get magnetometer out of low power mode

        def __twos_comp_combine(self, msb, lsb):
            value = (256*msb) + lsb

            if value & 0x8000:
                value = ~value + 1

            return value

        def get_acceleration(self):
            acceleration_x = self.__twos_comp_combine(self.__i2c_bus.read_byte_data(LSM, ACC_X_MSB),
                                                      self.__i2c_bus.read_byte_data(LSM, ACC_X_LSB))
            acceleration_y = self.__twos_comp_combine(self.__i2c_bus.read_byte_data(LSM, ACC_Y_MSB),
                                                      self.__i2c_bus.read_byte_data(LSM, ACC_Y_LSB))
            acceleration_z = self.__twos_comp_combine(self.__i2c_bus.read_byte_data(LSM, ACC_Z_MSB),
                                                      self.__i2c_bus.read_byte_data(LSM, ACC_Z_LSB))
            return (acceleration_x, acceleration_y, acceleration_z)

        def get_magnetic_field(self):
            magnetic_x = self.__twos_comp_combine(self.__i2c_bus.read_byte_data(LSM, MAG_X_MSB),
                                                  self.__i2c_bus.read_byte_data(LSM, MAG_X_LSB))
            magnetic_y = self.__twos_comp_combine(self.__i2c_bus.read_byte_data(LSM, MAG_Y_MSB),
                                                  self.__i2c_bus.read_byte_data(LSM, MAG_Y_LSB))
            magnetic_z = self.__twos_comp_combine(self.__i2c_bus.read_byte_data(LSM, MAG_Z_MSB),
                                                  self.__i2c_bus.read_byte_data(LSM, MAG_Z_LSB))
            return (magnetic_x, magnetic_y, magnetic_z)

    __instance = None

    def __init__(self):
        if not Orientation.__instance:
            Orientation.__instance = Orientation.__Orientation()

    def __getattr__(self, value):
        return getattr(self.__instance, value)

    def __setattr__(self, attr, value):
        return setattr(self.__instance, attr, value)