import socket
import threading
import logging
import datetime

class NetworkHandler:
    def __init__(self, in_port=4094):
        self.__network_socket = socket.socket(socket.AF_INET,
                                              socket.SOCK_DGRAM)
        self.__host = ""
        self.__callback_list = dict()
        self.__in_port = in_port
        self.__out_port = 0
        return

    def set_host(self, host, out_port=4092):
        self.__host = host
        self.__out_port = out_port

    def register_callback(self, function, command):
        """ Register callbacks, takes a function and a network command."""
        self.__callback_list[command] = function

    def send_command(self, command, *args):
        if self.__host:
            data = command + " "
            data += "; ".join(map(str, args))

            self.__network_socket.sendto(data.encode(),
                                         (self.__host, self.__out_port))

    def start(self):
        """ Starts the NetworkHandler, all callbacks needs to be registerd
        before this mathod is called. """
        logging.info("NH: Starting thread")
        self.thread = NetworkHandlerThread(self.__in_port,
                                           self.__callback_list)
        self.thread.start()

    def stop(self):
        self.thread.stop()


class NetworkHandlerThread(threading.Thread):
    """ Runs the network communication in a thread so that all other execution
    remains unaffected. """

    def __init__(self, port, callback_list):
        logging.info("NH: Thread created")
        threading.Thread.__init__(self)
        self.__stop = False
        self.__network_socket = socket.socket(socket.AF_INET,
                                              socket.SOCK_DGRAM)
        self.__port = port
        self.__callback_list = callback_list
        self.__network_socket.bind(('', self.__port))
        self.__network_socket.settimeout(0.2)

    def run(self):
        logging.info("NH: Thread started")
        while not self.__stop:
            try:
                data, _ =\
                    self.__network_socket.recvfrom(1024)
            except Exception:
                continue

            decoded_data = data.decode()

            if decoded_data == '':
                break
            else:
                splitted_data = decoded_data.split("; ")
                command = splitted_data[0]

                if len(splitted_data) > 1:
                    arguments = splitted_data[1:]
                else:
                    arguments = []

                if command in self.__callback_list:
                    logging.info("NH: Received command: {}".format(command))
                    self.__callback_list[command](*arguments)

                else:
                    logging.debug("NH: Received invalid command: {}"
                                  .format(command))

    def stop(self):
        self.__stop = True
