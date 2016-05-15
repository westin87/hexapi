class TestNetworkHandler:

    def setup(self):
        self.port = 12325
        self.nh = network_handler.NetworkHandler(self.port)

    @patch('hexarpi.network.network_handler.socket')
    def test_callback(self, mock_socket_module):
        self.mock_socket = MagicMock()
        mock_socket_module.socket = MagicMock(return_value=self.mock_socket)

        arguments = ["1337", "42"]
        command = "CALLBACK"
        data = "; ".join([command] + arguments)
        encoded_data = data.encode(encoding='utf_8', errors='strict')
        sender = ("ip", "port")

        self.mock_socket.recvfrom = MagicMock(
            return_value=(encoded_data, sender))

        callback = MagicMock()
        self.nh.register_callback(callback, "CALLBACK")
        self.nh.start()
        self.nh.stop()

        callback.assert_called_with(*arguments)