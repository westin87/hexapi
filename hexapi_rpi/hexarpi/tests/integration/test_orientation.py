from time import sleep

from hexarpi.utils.orientation import Orientation


def main():
    o = Orientation()

    while True:
        sleep(1)
        orientation_vector = o.get_euler_angel()
        print("Orientation vector: {}".format(orientation_vector))
        #print("Configuration status: {:08b}".format(o.get_calibration_status()))
        #print("System status: {:02X}".format(o.get_system_status()))
        #print("System error: {:02X}".format(o.get_system_error()))


if __name__ == '__main__':
    main()
