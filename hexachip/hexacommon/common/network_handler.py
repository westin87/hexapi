""" NetworkHandler module"""
import logging

import socket
import threading
import time


class NetworkHandler:
    """ Manages the network connection with the client. Other
    software registers callback functions together with a network command.
    The callback functions are then invoked when a matching network
    command is received from the client. The callback function can take
    any number of arguments. """

    def __init__(self, listen_port=4092):
        logging.info("NH: Network handler created, listening on port: {}".format(listen_port))
        self.thread = None
        self._listen_port = listen_port
        self._callback_container = dict()
        self._client = _Client()
        self._network_socket = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM)

    def start(self):
        """ Starts the NetworkHandler, all callbacks needs to be registerd
        before this mathod is called. """
        logging.info("NH: Starting thread")
        self.thread = NetworkHandlerThread(self._listen_port, self._client,
                                           self._callback_container)
        self.thread.start()

    def stop(self):
        self.thread.stop()

    def set_host(self, ip, port):
        self._client.ip = ip
        self._client.port = port

    def send_command(self, command, *args):
        if self._client.ip:
            data = _compose_command(command, args)

            self._network_socket.sendto(
                data.encode(), (self._client.ip, self._client.port))

    def register_callback(self, function, command):
        """ Register callbacks, takes a function and a network command."""
        self._callback_container[command] = function


class NetworkHandlerThread(threading.Thread):
    """ Runs the network communication in a thread so that all other execution
    remains unaffected. """

    def __init__(self, listen_port, client, callback_container):
        logging.info("NH: Thread created")
        threading.Thread.__init__(self)
        self._network_socket = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM)
        self._network_socket.bind(('', listen_port))
        self._network_socket.settimeout(0.2)

        self._stop_thread = False
        self._callback_container = callback_container
        self._client = client
        self._ping_checker = _PingChecker(self._command_abort)

    def run(self):
        logging.info("NH: Thread started")
        while not self._stop_thread:
            try:
                data, sender = self._network_socket.recvfrom(1024)
            except:
                continue

            self._client.client_ip = sender[0]

            if data:
                command, arguments = _parse_command(data)

                if command == "PING":
                    self._ping_checker.ping()

                elif command in self._callback_container:
                    logging.info(
                        "NH: Received command: " + command + " with arguments: " +
                        ", ".join(arguments))

                    self._callback_container[command](*arguments)

                else:
                    logging.warning("NH: Received invalid command: " + command)

    def stop(self):
        self._ping_checker.stop()
        self._stop_thread = True

    def _command_abort(self):
        self._callback_container.get('LAND', lambda: None)()


class _Client:
    def __init__(self, ip=None, port=None):
        if ip is not None:
            self.ip = ip
        else:
            self.ip = ""

        if port is not None:
            self.port = port
        else:
            self.port = 4093


class _PingChecker(threading.Thread):
    def __init__(self, abort_callback):
        threading.Thread.__init__(self)
        self._abort_callback = abort_callback
        self._stop_thread = False
        self._first_ping = True
        self._last_ping_time = 0

    def ping(self):
        self._last_ping_time = time.time()

        if self._first_ping:
            self.start()
            self._first_ping = False

    def run(self):
        while not self._stop_thread:
            if abs(self._last_ping_time - time.time()) > 4:
                logging.info("NH: Network connection lost")
                self._stop_thread = True
                self._abort_callback()
            time.sleep(1)

    def stop(self):
        self._stop_thread = True


def _compose_command(command, args):
    data = command
    if args:
        data += "; " + "; ".join(map(str, args))
    return data


def _parse_command(data):
    data = data.decode()
    data_list = list(map(str.strip, data.split("; ")))

    command = data_list[0]
    arguments = data_list[1:] if len(data_list) > 1 else []
    return command, arguments
