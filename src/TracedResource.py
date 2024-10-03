import matplotlib.pyplot as plt
from simpy import Resource
from operator import itemgetter
import numpy as np


class TracedResource(Resource):

    def __init__(self, env, capacity, name="Unnamed Resource", accociated_node=None):
        super().__init__(env, capacity)
        self.env = env
        self.name = name
        self.node = accociated_node

        self.log_event = []
        self.log_time = []

        self.customer_queue = [] # custom queue for finding customer information in the queue

        self.ucids = set({})

    def request(self, customer=None):
        self.log_event.append(1)
        self.log_time.append(self.env.now)
        if customer is not None:
            self.customer_queue.append(customer)
        return super().request()

    def release(self, request):
        self.log_event.append(-1)
        self.log_time.append(self.env.now)
        if len(self.customer_queue) > 0:
            self.customer_queue.pop(0)
        return super().release(request)

    def availability(self):
        demand = np.cumsum(np.asarray(self.log_event))
        available = self.capacity - demand
        return available, np.asarray(self.log_time)

    def queue_length(self):
        available, time = self.availability()
        available[available > 0] = 0
        return available * -1, time

    def plot_availability(self):
        fig, ax = plt.subplots()

        availability, time = self.availability()

        ax.step(time, np.append(availability, availability[-1])[:-1], where='post')  # piecewise constant
        ax.axhline(0, color='k', linestyle='dashed')

        ax.set_xlabel("time [s]")
        ax.set_ylabel("{} availability".format(self.name))
        # ax.legend()

        ymin, ymax = ax.get_ylim()
        ax.axhspan(ymin=ymin, ymax=0, facecolor='r', alpha=0.25)
        ax.axhspan(ymin=0, ymax=ymax, facecolor='g', alpha=0.25)
        ax.set_ylim(ymin, ymax)
        ax.set_xlim(0, max(time))

        ax.grid(True)
        plt.show()
