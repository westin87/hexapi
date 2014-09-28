""" NetworkHandler module"""
import socket
import threading
import time


class NetworkHandler:
    """ Manages the network connection with the client. Other
    software registers callback functions together with a network command.
    The callback functions are then invoked when a matching network
    command is received from the client. The callback function can take
    any number of arguments. """

    def __init__(self, port):
        print "NH: Network handler created"
        self.port = port
        self.callback_list = {}

    def register_callback(self, fPtr, command):
        """ Register callbacks, takes a function and a network command."""
        self.callback_list[command] = fPtr

    def start(self):
        """ Starts the NetworkHandler, all callbacks needs to be registerd
        before this mathod is called. """
        print "NH: Starting thread"
        self.thread = NetworkHandlerThread(self.port, self.callback_list)
        self.thread.start()

    def stop(self):
        self.thread.stop()


class PingChecker(threading.Thread):
    def __init__(self, last_ping_time, abort_callback):
        threading.Thread.__init__(self)
        self.__last_ping_time = last_ping_time
        self.__abort_callback = abort_callback
        self.__stop = False

    def run(self):
        while not self.__stop:
            if abs(self.__last_ping_time[0] - time.time()) > 4:
                print "NH: Network connection lost"
                self.__stop = True
                self.__abort_callback()
            time.sleep(1)

    def stop(self):
        self.__stop = True


class NetworkHandlerThread(threading.Thread):
    """ Runs the network communication in a thread so that all other execution
    remains unaffected. """

    def __init__(self, port, callback_list):
        print "NH: Thread created"
        threading.Thread.__init__(self)
        self.__stop = False
        self.__network_socket = socket.socket(socket.AF_INET,
                                              socket.SOCK_DGRAM)
        self.__port = port
        self.__callback_list = callback_list
        self.__network_socket.bind(('', self.__port))
        self.__network_socket.setblocking(0)
        self.__client = None
        self.__address = None
        self.__first_ping = True
        self.__time_of_last_ping = [0]
        self.__ping_checker = PingChecker(self.__time_of_last_ping,
                                          self.__command_abort)

    def __command_abort(self):
        self.__callback_list['LAND']()

    def run(self):
        print "NH: Thread started"
        while not self.__stop:
            try:
                data, _ = self.__network_socket.recvfrom(1024)
            except Exception:
                continue

            decoded_data = data.decode()

            if decoded_data == '':
                break
            else:
                splitted_data = decoded_data.split()
                command = splitted_data[0]

                if len(splitted_data) > 1:
                    arguments = splitted_data[1:]
                else:
                    arguments = []

                if command == "PING":

                    self.__time_of_last_ping[0] = time.time()

                    if self.__first_ping:
                        self.__ping_checker.start()
                        self.__first_ping = False

                elif command in self.__callback_list:
                    print "NH: Client sent command: " + command
                    self.__callback_list[command](*arguments)

                else:
                    print "NH: Client sent invalid command: " + command

    def stop(self):
        self.__ping_checker.stop()
        self.__stop = True
