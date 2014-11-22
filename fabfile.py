#!/usr/bin/python2

from fabric.api import run, put, sudo


def deploy():
    run("rm -rf /home/$USER/code/hexapi_rpi")
    put("hexapi_rpi", "/home/$USER/code")


def start_gps():
    sudo("gpsd /dev/ttyAMA0")


def start_3g_modem():
    pass


def start_hexapi():
    sudo("/home/$USER/code/hexapi_rpi/rpi.py >> "
         "/home/$USER/code/hexapi_rpi/rpi.log")
