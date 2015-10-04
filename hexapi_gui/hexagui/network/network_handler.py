import socket
import threading
import logging
import datetime


class NetworkHandler:
    def __init__(self, in_port=4094):
        self._network_socket = socket.socket(socket.AF_INET,
                                              socket.SOCK_DGRAM)
        self.thread = None
        self._host = ""
        self._callback_container = dict()
        self._in_port = in_port
        self._out_port = 0
        return

    def set_host(self, host, out_port=4092):
        self._host = host
        self._out_port = out_port

    def register_callback(self, function, command):
        """ Register callbacks, takes a function and a network command."""
        self._callback_container[command] = function

    def send_command(self, command, *args):
        if self._host:
            logging.info("NH: Sending command: {}".format(command))

            data = command
            if args:
                data += "; " + "; ".join(map(str, args))

            self._network_socket.sendto(data.encode(),
                                        (self._host, self._out_port))

    def start(self):
        """ Starts the NetworkHandler, all callbacks needs to be registerd
        before this mathod is called. """
        logging.info("NH: Starting thread")
        self.thread = NetworkHandlerThread(self._in_port,
                                           self._callback_container)
        self.thread.start()

    def stop(self):
        self.thread.stop()


class NetworkHandlerThread(threading.Thread):
    """ Runs the network communication in a thread so that all other execution
    remains unaffected. """

    def __init__(self, port, callback_container):
        logging.info("NH: Thread created")
        threading.Thread.__init__(self)
        self._stop = False
        self._network_socket = socket.socket(socket.AF_INET,
                                             socket.SOCK_DGRAM)
        self._port = port
        self._callback_container = callback_container
        self._network_socket.bind(('', self._port))
        self._network_socket.settimeout(0.2)

    def run(self):
        logging.info("NH: Thread started")
        while not self._stop:
            try:
                data, _ = \
                    self._network_socket.recvfrom(1024)
            except Exception:
                continue

            decoded_data = data.decode()

            if decoded_data != '':
                splitted_data = [e for e in
                                 map(str.strip, decoded_data.split("; "))]

                command = splitted_data[0]

                arguments = splitted_data[1:] if len(splitted_data) > 1 else []

                if command in self._callback_container:
                    logging.info("NH: Received command: {}".format(command))
                    self._callback_container[command](*arguments)

                else:
                    logging.debug("NH: Received invalid command: {}"
                                  .format(command))

    def stop(self):
        self._stop = True
