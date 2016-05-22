from unittest.mock import MagicMock, patch

from hexacommon.common.communication import Communication


class TestNetworkHandler:

    def setup(self):
        self.port = 12325
        self.nh = Communication(self.port)

    @patch('hexachip.hexacommon.common.network_handler.socket')
    def test_callback(self, mock_socket_module):
        self.mock_socket = MagicMock()
        mock_socket_module.socket = MagicMock(return_value=self.mock_socket)

        arguments = ["1337", "42", "123"]
        command = "CALLBACK"
        data = "; ".join([command] + arguments)
        encoded_data = data.encode(encoding='utf_8', errors='strict')
        sender = ("ip", "port")

        self.mock_socket.recvfrom = MagicMock(
            return_value=(encoded_data, sender))

        callback = MagicMock()
        self.nh.connect_command_callback(callback, "CALLBACK")
        self.nh.start()
        self.nh.stop()

        callback.assert_called_with(*arguments)