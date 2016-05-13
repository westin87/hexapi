from time import sleep

from hexarpi.utils.orientation import Orientation


def main():
    o = Orientation()

    while True:
        sleep(1)
        orientation_vector = o.get_euler_angel()
        print("Orientation vector: {}".format(orientation_vector))

if __name__ == '__main__':
    main()
