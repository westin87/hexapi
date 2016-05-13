from hexarpi.network import network_handler
from mock import patch, MagicMock

from hexarpi.utils import movement


class TestSetMovements:

    @patch('hexarpi.utils.movement.ada')
    def setup(self, mock_pwm_module):
        self.mock_pwm = MagicMock()
        mock_pwm_module.PWM = MagicMock(return_value=self.mock_pwm)
        self.move = movement.Movement(50)

    def teardown(self):
        del self.move

    def test_set_pitch_0(self):
        self.move.set_pitch(0)

        self.mock_pwm.set_pwm.assert_called_with(1, 0, 307)

        self.teardown()

    def test_set_pitch_100(self):
        self.move.set_pitch(100)

        self.mock_pwm.set_pwm.assert_called_with(1, 0, 409)

        self.teardown()

    def test_set_pitch_minus_100(self):
        self.move.set_pitch(-100)

        self.mock_pwm.set_pwm.assert_called_with(1, 0, 204)


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
