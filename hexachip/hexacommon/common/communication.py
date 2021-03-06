""" NetworkHandler module"""
import logging

import socket
import threading
import time


class Communication:
    """ Manages the network connection with the client. Other
    software registers callback functions together with a network command.
    The callback functions are then invoked when a matching network
    command is received from the client. The callback function can take
    any number of arguments. """

    def __init__(self, in_port=4092, out_port=4094, out_socket=None, in_socket=None):
        logging.info("NH: Network handler created, listening on port: {}".format(in_port))
        self._receiver_thread = None
        self._listen_port = in_port
        self._callback_container = dict()
        self._client = _Client(port=out_port)

        if out_socket is None:
            self._network_socket = socket.socket(
                socket.AF_INET, socket.SOCK_DGRAM)
        else:
            self._network_socket = out_socket

        self._receiver_thread = _ReceiverThread(
            self._listen_port, self._client, self._callback_container,
            in_socket=in_socket)

    def start(self):
        """ Starts the NetworkHandler, all callbacks needs to be registerd
        before this mathod is called. """
        logging.info("NH: Starting thread")
        self._receiver_thread.start()

    def stop(self):
        self._receiver_thread.stop()

    def set_host(self, ip, port):
        self._client.ip = ip
        self._client.port = port

    def send_command(self, command, *args, **kwargs):
        if self._client.ip and self._client.port:
            data = _compose_command(command, args, kwargs)

            self._network_socket.sendto(
                data.encode(), (self._client.ip, self._client.port))

    def connect_command_callback(self, function, command):
        """ Register callbacks, takes a function and a network command."""
        self._callback_container[command] = function


class _ReceiverThread(threading.Thread):
    """ Runs the network communication in a thread so that all other execution
    remains unaffected. """

    def __init__(self, listen_port, client, callback_container, in_socket=None):
        logging.info("NH: Thread created")
        threading.Thread.__init__(self)

        if in_socket is None:
            self._network_socket = socket.socket(
                socket.AF_INET, socket.SOCK_DGRAM)
        else:
            self._network_socket = in_socket
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

            self._client.ip = sender[0]

            if data:
                command, args, kwargs = _parse_command(data)

                if command == "PING":
                    self._ping_checker.ping()

                elif command in self._callback_container:
                    logging.info(
                        "NH: Received command: {} with arguments: {}, {}".format(
                            command, args, kwargs))

                    try:
                        self._callback_container[command](*args, **kwargs)
                    except AttributeError:
                        logging.error("Invalid attributes for command: {}, received arguments: {}, {}".format(
                            command, args, kwargs))

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
            self.port = 4000

    def __str__(self):
        return "Client: ip: {}, port: {}".format(self.ip, self.port)


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


def _compose_command(command, args=None, kwargs=None):
    data = command

    if args:
        data += "; " + "; ".join(map(str, args))

    if kwargs:
        data += "; "
        for key, argument in kwargs.items:
            data += "{}={}".format(key, argument)

    return data


def _parse_command(data):
    data = data.decode()
    data_list = list(map(str.strip, data.split("; ")))

    command = data_list[0]
    argument_list = data_list[1:] if len(data_list) > 1 else []

    args = list()
    kwargs = dict()

    for argument in argument_list:
        if '=' in argument:
            key, value = argument.split('=')
            kwargs[key] = value
        else:
            args.append(argument)

    return command, args, kwargs
