from src.TracedResource import TracedResource
from scipy.stats import truncnorm

import numpy as np


class Department:

    def __init__(self, name, env, queue=None, times=None, node=None, shelves=[]):
        self.name = name
        self.env = env

        self.log_event = []
        self.log_time = []

        if queue is not None and times is not None:
            self.queue = TracedResource(env, capacity=queue, name=name, accociated_node=node)
            self.rv = truncnorm(-4, 4, loc=times[0], scale=times[1])
        else:
            self.queue = None
            self.times = None

        self.shelves = shelves

        self.probabilities = np.asarray([s.length for s in self.shelves])
        self.probabilities /= np.sum(self.probabilities)

    def scale(self, old, new):
        # scale using old and new extends of the store
        for shelf in self.shelves:
            shelf.scale(old, new)

    def get_item_location(self, rng):
        shelf = rng.choice(self.shelves, p=self.probabilities)
        return shelf.relative_position(rng.uniform(0 , 1))

    def customers_inside(self):
        return np.cumsum(np.asarray(self.log_event)), np.asarray(self.log_time)
