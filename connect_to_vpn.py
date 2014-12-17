#!/usr/bin/env python3

import urllib.request
import os
import subprocess
import time
import socket


def is_connected():
    try:
        urllib.request.urlopen("http://74.125.232.102/", timeout=3)
        return True
    except (urllib.request.URLError, socket.timeout):
        return False


def is_process_alive(pid):
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def connect_to_vpn():
    file_path = "/tmp/hex92518"
    if not os.path.exists(file_path) and is_connected():
        print("---- {} - Connecting to VPN ----".format(time.ctime()))
        command = ["sudo", "openvpn", "/home/pi/vpn/client.ovpn"]
        print("Running command: {}\n".format(" ".join(command)))
        proc = subprocess.Popen(command)
        with open(file_path, 'w') as pid_file:
            pid_file.write(str(proc.pid))
    else:
        with open(file_path, 'r') as pid_file:
            pid = int(pid_file.read())
        if not is_process_alive(pid):
            print("---- {} - Reconnecting to VPN in 60s ----\n".format(time.ctime()))
            os.remove(file_path)


if __name__ == '__main__':
    connect_to_vpn()
