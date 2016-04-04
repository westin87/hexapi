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


class PDRegulator:
    def __init__(self, k, td, samples=20, absolute=True):
        self.k = k
        self.td = td

        self._deriver = Deriver(samples)

        self._absolute = absolute

    def update(self, R, Y):

        u = self.k * (R - Y) + self.td * self._deriver.derive(R - Y)

        if self._absolute:
            u = abs(u)

        return np.clip(u, 0, 0.2)