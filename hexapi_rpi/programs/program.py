import utils.movement as movement


class Program(object):
    """docstring for Program"""
    def __init__(self):
        self._mov = movement.Movement(50)
        self._stop_program = False

    def stop(self):
        self._stop_program = True
