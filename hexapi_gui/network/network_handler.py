import socket


class NetworkHandler:
    def __init__(self):
        self.__network_socket = socket.socket(socket.AF_INET,
                                              socket.SOCK_DGRAM)
        self.__host = ""
        self.__port = 0
        return

    def set_host(self, host, port):
        self.__host = host
        self.__port = port

    def send_command(self, command, *args):
        if self.__host:
            data = command + " "
            for arg in args:
                data += (str(arg) + " ")

            self.__network_socket.sendto(data.encode(),
                                         (self.__host, self.__port))
