#!/usr/bin/python2

from fabric.api import run, put, sudo, env


env.user = "pi"
env.hosts = ["192.169.1.2"]


def deploy():
    run("rm -rf /home/$USER/code/hexapi_rpi")
    put("hexapi_rpi", "/home/$USER/code/")


def start_gps():
    sudo("nohup gpsd /dev/ttyAMA0")


def start_hexapi():
    sudo("nohup /home/$USER/code/hexapi_rpi/rpi.py >> "
         "/home/$USER/code/hexapi_rpi/rpi.log")


def test():
    run("ls")
