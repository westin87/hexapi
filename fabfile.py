#!/usr/bin/python2

import os

from fabric.api import run, put, env, get


env.user = "pi"
env.hosts = ["192.169.1.2"]


def deploy():
    run("rm -rf /home/pi/code/hexapi_rpi")
    put("hexapi_rpi", "/home/pi/code/")
    run("sudo chmod u+x /home/pi/code/hexapi_rpi/rpi.py")


def start_gps():
    run("sudo gpsd /dev/ttyAMA0")


def get_gps_data():
    get("/home/pi/code/hexapi_rpi/utils/gps_data.log", ".")


def start_hexapi():
    run("nohup sudo /home/pi/code/hexapi_rpi/rpi.py >> "
        "/home/pi/code/hexapi_rpi/rpi.log")


def test():
    run("ls")
