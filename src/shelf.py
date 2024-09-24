import numpy as np


class Shelf:

    def __init__(self, start, end):
        self.start = start
        self.end = end

    @property
    def delta(self):
        return self.end - self.start

    @property
    def length(self):
        return np.linalg.norm(self.delta)

    def scale(self, old, new):
        # scale using old and new extends of the store
        self.start = self.start / old * new
        self.end = self.end / old * new

    def relative_position(self, loc):
        return self.start + loc * self.delta