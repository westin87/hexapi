#!/usr/bin/env python3

import urllib.request
import subprocess
import time
import socket


def is_connected():
    try:
        urllib.request.urlopen("http://74.125.232.102/", timeout=3)
        return True
    except (urllib.request.URLError, socket.timeout):
        return False


def connect_3g_modem():
    if not is_connected():
        print("---- {} - Connecting to 3G ----".format(time.ctime()))
        command = ["sudo", "sakis3g", "connect", "USBINTERFACE=0"]
        print("Running command: {}".format(" ".join(command)))
        proc = subprocess.Popen(command, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        proc.wait()
        if proc.stdout:
            print("Stdout: {}".format(proc.stdout.read()))
        if proc.stderr:
            print("Stderr: {}".format(proc.stderr.read()))
        print("\n")


if __name__ == '__main__':
    connect_3g_modem()
