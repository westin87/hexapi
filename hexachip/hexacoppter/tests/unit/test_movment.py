from unittest.mock import MagicMock

from hexachip.hexacoppter.utils import movement


class TestSetMovements:
    def setup(self):
        self.pwm_drier_mock = MagicMock()
        self.move = movement.Movement(50, pwm_driver=self.pwm_drier_mock)

    def test_set_pitch_0(self):
        self.move.set_pitch(0)

        # 0 servo position = 1.5 ms duty cycle =>
        # => number of ticks = 1.5 ms / tick length, where tick length = 20 / 4096 =  307
        self.pwm_drier_mock.set_pwm.assert_called_with(1, 0, 307)

    def test_set_pitch_100(self):
        self.move.set_pitch(100)

        # Max servo position = 2.5 ms duty cycle => number of ticks = 409
        self.pwm_drier_mock.set_pwm.assert_called_with(1, 0, 409)

    def test_set_pitch_minus_100(self):
        self.move.set_pitch(-100)

        # Min servo position = 0.5 ms duty cycle => number of ticks = 204
        self.pwm_drier_mock.set_pwm.assert_called_with(1, 0, 204)


