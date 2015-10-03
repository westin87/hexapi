""" NetworkHandler module"""
import socket
import threading
import time

from hexacommon.common import singleton


class SharedData():
    last_ping_time = 0
    client_ip = ""


class NetworkHandler():
    """ Manages the network connection with the client. Other
    software registers callback functions together with a network command.
    The callback functions are then invoked when a matching network
    command is received from the client. The callback function can take
    any number of arguments. """

    def __init__(self, in_port=4092, out_port=4094):
        print "NH: Network handler created"
        self.thread = None
        self._in_port = in_port
        self._out_port = out_port
        self._callback_list = dict()
        self._shared_data = SharedData()
        self._network_socket = socket.socket(socket.AF_INET,
                                              socket.SOCK_DGRAM)

    def register_callback(self, function, command):
        """ Register callbacks, takes a function and a network command."""
        self._callback_list[command] = function

    def send_command(self, command, *args):
        if self._shared_data.client_ip:
            data = command
            if args:
                data += "; " + "; ".join(map(str, args))

            self._network_socket.sendto(data.encode(),
                                         (self._shared_data.client_ip,
                                          self._out_port))

    def start(self):
        """ Starts the NetworkHandler, all callbacks needs to be registerd
        before this mathod is called. """
        print "NH: Starting thread"
        self.thread = NetworkHandlerThread(self._in_port, self._shared_data,
                                           self._callback_list)
        self.thread.start()

    def stop(self):
        self.thread.stop()


class PingChecker(threading.Thread):
    def __init__(self, shared_data, abort_callback):
        threading.Thread.__init__(self)
        self.__shared_data = shared_data
        self.__abort_callback = abort_callback
        self.__stop = False

    def run(self):
        while not self.__stop:
            if abs(self.__shared_data.last_ping_time - time.time()) > 4:
                print "NH: Network connection lost"
                self.__stop = True
                self.__abort_callback()
            time.sleep(1)

    def stop(self):
        self.__stop = True


class NetworkHandlerThread(threading.Thread):
    """ Runs the network communication in a thread so that all other execution
    remains unaffected. """

    def __init__(self, port, shared_data,  callback_list):
        print "NH: Thread created"
        threading.Thread.__init__(self)
        self._stop = False
        self._network_socket = socket.socket(socket.AF_INET,
                                             socket.SOCK_DGRAM)
        self._port = port
        self._callback_list = callback_list
        self._network_socket.bind(('', self._port))
        self._network_socket.settimeout(0.2)
        self._first_ping = True
        self._shared_data = shared_data
        self._ping_checker = PingChecker(self._shared_data,
                                          self._command_abort)

    def _command_abort(self):
        do_nothing = lambda x: 0
        self._callback_list.get('LAND', do_nothing)()

    def run(self):
        print "NH: Thread started"
        while not self._stop:
            try:
                data, sender =\
                    self._network_socket.recvfrom(1024)
            except Exception:
                continue

            self._shared_data.client_ip = sender[0]

            decoded_data = data.decode()

            if decoded_data:
                splitted_data = map(unicode.strip, decoded_data.split("; "))
                command = splitted_data[0]

                arguments = splitted_data[1:] if len(splitted_data) > 1 else []

                if command == "PING":

                    self._shared_data.last_ping_time = time.time()

                    if self._first_ping:
                        self._ping_checker.start()
                        self._first_ping = False

                elif command in self._callback_list:
                    print "NH: Received command: " + command +\
                          " with arguments: " + ", ".join(arguments)

                    self._callback_list[command](*arguments)

                else:
                    print "NH: Received invalid command: " + command

    def stop(self):
        self._ping_checker.stop()
        self._stop = True
