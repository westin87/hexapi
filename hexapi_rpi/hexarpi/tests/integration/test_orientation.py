from time import sleep

from hexarpi.utils.orientation import Orientation


def main():
    o = Orientation()

    while range(10):
        sleep(1)
        orientation_vector = o.get_euler_angel()
        print orientation_vector


if __name__ == '__main__':
    main()
