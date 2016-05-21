class BaseProgram:
    """docstring for Program"""
    def __init__(self, communication, movement):
        self._communication = communication
        self._move = movement
        self._stop_program = False

    def stop(self):
        self._stop_program = True
