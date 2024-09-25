from src.TracedResource import TracedResource
from scipy.stats import truncnorm
import numpy as np

class Department:

    def __init__(self, name, env, queue=None, times=None):
        self.name = name
        self.env = env

        self.log_event = []
        self.log_time = []

        if queue is not None and times is not None:
            self.queue = TracedResource(env, capacity=queue, name=name)
            self.rv = truncnorm(-4, 4, loc=times[0], scale=times[1])
        else:
            self.queue = None
            self.times = None

        def customers_inside(self):
            cusinside = np.cumsum(np.asarray(self.log_event))
            return cusinside, np.asarray(self.log_time)
