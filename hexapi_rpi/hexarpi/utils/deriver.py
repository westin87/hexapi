import numpy as np


class Deriver:
    def __init__(self, samples):
        self._samples = samples
        self._saved_values = np.array([])

    def derive(self, y):
        self._saved_values = np.append(self._saved_values, y)

        if len(self._saved_values) > self._samples:
            derivative = np.mean(self._saved_values[1:] - self._saved_values[:-1])
            self._saved_values = np.delete(self._saved_values, 0)
        else:
            derivative = 0

        return derivative
