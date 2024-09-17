from src.TracedResource import TracedResource
from scipy.stats import truncnorm


class Department:

    def __init__(self, name, env, queue=None, times=None):
        self.name = name
        self.env = env

        if queue is not None and times is not None:
            self.queue = TracedResource(env, capacity=queue, name=name)
            self.rv = truncnorm(-4, 4, loc=times[0], scale=times[1])
        else:
            self.queue = None
            self.times = None
