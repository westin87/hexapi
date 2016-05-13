class Program(object):
    """docstring for Program"""
    def __init__(self, movement, network_handler):
        self._mov = movement
        self._nh = network_handler
        self._stop_program = False

    def stop(self):
        self._stop_program = True
