#!/usr/bin/python2

import os

from fabric.api import run, put, env, get, local, cd

env.user = "pi"
env.hosts = ["192.168.1.12"]

pi_home = "/home/pi/code/"


def deploy():
    run("sudo rm -rf {}".format(os.path.join(pi_home, "hexapi_common")))
    run("sudo rm -rf {}".format(os.path.join(pi_home, "hexapi_rpi")))

    with open("resources/directories_to_make.txt") as fo:
        directories_to_make = fo.readlines()

    directories_to_make = map(str.strip, directories_to_make)

    for directory in directories_to_make:
        if directory:
            run("mkdir {}".format(os.path.join(pi_home, directory)))

    with open("resources/files_to_deploy.txt") as fo:
        files_to_move = fo.readlines()

    files_to_move = map(str.strip, files_to_move)

    for file_path in files_to_move:
        if file_path:
            put(file_path, os.path.join(pi_home, file_path))

    with cd(os.path.join(pi_home, "hexapi_common")):
        run("sudo python setup.py install")

    with cd(os.path.join(pi_home, "hexapi_rpi")):
        run("sudo python setup.py install")

def start_gps():
    run("sudo gpsd /dev/ttyAMA0")


def get_log_data():
    get("/home/pi/hexapi_logs", ".")


def start_hexapi():
    run("nohup sudo hexarpi >> /home/pi/hexapi_logs/rpi.log")


def test():
    print env.hosts
    run("ls")
