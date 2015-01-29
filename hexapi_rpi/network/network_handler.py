""" NetworkHandler module"""
import socket
import threading
import time


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
        self.__in_port = in_port
        self.__out_port = out_port
        self.__callback_list = dict()
        self.__shared_data = SharedData()
        self.__network_socket = socket.socket(socket.AF_INET,
                                              socket.SOCK_DGRAM)

    def register_callback(self, function, command):
        """ Register callbacks, takes a function and a network command."""
        self.__callback_list[command] = function

    def send_command(self, command, *args):
        if self.__shared_data.client_ip:
            data = command + "; "
            data += "; ".join(map(str, args))
            self.__network_socket.sendto(data.encode(),
                                         (self.__shared_data.client_ip,
                                          self.__out_port))

    def start(self):
        """ Starts the NetworkHandler, all callbacks needs to be registerd
        before this mathod is called. """
        print "NH: Starting thread"
        self.thread = NetworkHandlerThread(self.__in_port, self.__shared_data,
                                           self.__callback_list)
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
        self.__stop = False
        self.__network_socket = socket.socket(socket.AF_INET,
                                              socket.SOCK_DGRAM)
        self.__port = port
        self.__callback_list = callback_list
        self.__network_socket.bind(('', self.__port))
        self.__network_socket.settimeout(0.2)
        self.__first_ping = True
        self.__shared_data = shared_data
        self.__ping_checker = PingChecker(self.__shared_data,
                                          self.__command_abort)

    def __command_abort(self):
        do_nothing = lambda x: 0
        self.__callback_list.get('LAND', do_nothing)()

    def run(self):
        print "NH: Thread started"
        while not self.__stop:
            try:
                data, sender =\
                    self.__network_socket.recvfrom(1024)
            except Exception:
                continue

            self.__shared_data.client_ip = sender[0]

            decoded_data = data.decode()

            if decoded_data == '':
                break
            else:
                splitted_data = map(unicode.strip, decoded_data.split("; "))
                command = splitted_data[0]

                if len(splitted_data) > 1:
                    arguments = splitted_data[1:]
                else:
                    arguments = []

                if command == "PING":

                    self.__shared_data.last_ping_time = time.time()

                    if self.__first_ping:
                        self.__ping_checker.start()
                        self.__first_ping = False

                elif command in self.__callback_list:
                    print "NH: Received command: " + command
                    self.__callback_list[command](*arguments)

                else:
                    print "NH: Received invalid command: " + command

    def stop(self):
        self.__ping_checker.stop()
        self.__stop = True
