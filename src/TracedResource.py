import matplotlib.pyplot as plt
from simpy import Resource
from operator import itemgetter
import numpy as np


class TracedResource(Resource):

    def __init__(self, env, capacity, name="Unnamed Resource"):
        super().__init__(env, capacity)
        self.env = env
        self.name = name

        self.log_event = []
        self.log_time = []

        self.queueLog = []
        self.capacityLog = []
        self.demandLog = []
        self.ucids = set({})

    def request(self):
        self.log_event.append(1)
        self.log_time.append(self.env.now)
        return super().request()

    def release(self, request):
        self.log_event.append(-1)
        self.log_time.append(self.env.now)
        return super().release(request)

    def request_block(self, customer, subprocess):
        """
        wrapper around the .request() method, including the logging of relevant events
        function essentially replaces the "with self.request() as req:" block
        WARNING: implement with caution, as the request block has to be:
         1) wrapped in the env.process() function
         2) yielded when executing
         see implementation in the checkoutQueue, breadQueue, and cheeseQueue for reference
        :param customer: a Customer class instance
        :param subprocess: any env.process
        """
        self.ucids.add(customer.ucid)  # add ucid to set of users of this resource

        req = self.request()

        if customer.flags["print"]:
            print('{:.2f}: {} enters a {} queue'.format(self.env.now, customer.ucid, self.name))

        t0 = self.env.now
        self.queueLog.append(
            {
                "ucid": customer.ucid,
                "time": t0,
                "value": 1
            }
        )
        self.demandLog.append(
            {
                "ucid": customer.ucid,
                "time": t0,
                "value": 1
            }
        )
        yield req  # wait to be served
        t1 = self.env.now
        # queueLog queue exit
        self.queueLog.append(
            {
                "ucid": customer.ucid,
                "time": t1,
                "value": -1
            }
        )
        customer.wait_times[self.name] = t1 - t0

        if customer.flags["print"]:
            print('{:.2f}: {} is served at {}'.format(self.env.now, customer.ucid, self.name))

        # log use
        self.capacityLog.append(
            {
                "ucid": customer.ucid,
                "time": t1,
                "value": 1
            }
        )

        yield subprocess

        self.release(req)

        t2 = self.env.now

        # log end of use
        self.capacityLog.append(
            {
                "ucid": customer.ucid,
                "time": t2,
                "value": -1
            }
        )
        self.demandLog.append(
            {
                "ucid": customer.ucid,
                "time": t2,
                "value": -1
            }
        )
        customer.use_times[self.name] = t2 - t1

    def postprocess_log(self, log):
        time = np.array([el["time"] for el in log])
        entries = np.array([el["value"] for el in log])
        cs = np.cumsum(entries)

        indices = np.where([time[i + 1] == time[i] for i in range(len(time) - 2)])
        cs = np.delete(cs, indices[0])
        time = np.delete(time, indices[0])

        return cs, time

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

    def get_wait_time(self, ucid: int):
        timestamps = [logEntry["time"] for logEntry in self.queueLog if logEntry["ucid"] == ucid]
        if timestamps:
            return timestamps[-1] - timestamps[0]
        else:
            return 0

    def get_use_time(self, ucid: int):
        timestamps = [logEntry["time"] for logEntry in self.capacityLog if logEntry["ucid"] == ucid]
        return timestamps[-1] - timestamps[0]

    def wait_time_dictionary(self):
        ret = {}
        for ucid in self.ucids:
            ret[str(ucid)] = self.get_wait_time(ucid)

        return ret

    def use_time_dictionary(self):
        ret = {}
        for ucid in self.ucids:
            ret[str(ucid)] = self.get_use_time(ucid)

        return ret

    def average_wait_time(self):
        data = self.wait_time_dictionary()
        ave = sum([val for key, val in data.items()]) / len(data)
        return ave

    def average_use_time(self):
        data = self.use_time_dictionary()
        ave = sum([val for key, val in data.items()]) / len(data)
        return ave

    def wait_time_histogram(self):

        fig, ax = plt.subplots()
        data = self.wait_time_dictionary()

        ax.hist(data.values(), bins=25)

        ax.set_ylabel("no. of {} users".format(self.name))
        ax.set_xlabel("wait time [s]")
        ax.legend()

        ax.grid(True)
        plt.show()

    def use_time_histogram(self):

        fig, ax = plt.subplots()
        data = self.use_time_dictionary()

        ax.hist(data.values(), bins=25)

        ax.set_ylabel("no. of {} users".format(self.name))
        ax.set_xlabel("use time [s]")
        ax.legend()

        ax.grid(True)
        plt.show()


def checkout_process(customer, env):
    t_tot_scan = 0.

    # scan each item
    for n_item in range(customer.total_items()):
        t_scan = float(
            customer.rng.normal(customer.stochastics["scan_vars"][0], customer.stochastics["scan_vars"][1], 1))
        t_tot_scan += t_scan
        yield env.timeout(t_scan)

    if customer.flags["print"]:
        print('{:.2f}: {} scans items at checkout'.format(env.now, customer.ucid))

    # payment
    t_pay = float(
        customer.rng.uniform(customer.stochastics["payment_bounds"][0], customer.stochastics["payment_bounds"][1], 1))
    yield env.timeout(t_pay)

    if customer.flags["print"]:
        print('{:.2f}: {} pays at checkout'.format(env.now, customer.ucid))


def checkout_queues(customer, env, checkouts):
    # access checkout queues to see which is the quickest
    queue_lengths = [
        len(ch.put_queue) + ch.count for ch in checkouts
    ]

    # find the index of the shortest queue
    index, element = min(enumerate(queue_lengths), key=itemgetter(1))

    # enter the shortest queue
    subprocess = env.process(checkout_process(customer, env))
    req_block = env.process(checkouts[index].request_block(customer, subprocess))
    yield req_block


def bread_process(customer, env):
    t_bread = float(
        customer.rng.normal(customer.stochastics["bread_vars"][0], customer.stochastics["bread_vars"][1], 1))
    yield env.timeout(t_bread)

    if customer.flags["print"]:
        print('{:.2f}: {} is served at department C'.format(env.now, customer.ucid))


def bread_queue(customer, env, bread_clerks):
    subprocess = env.process(bread_process(customer, env))
    req_block = env.process(bread_clerks.request_block(customer, subprocess))
    yield req_block


def cheese_process(customer, env):
    t_cheese = float(
        customer.rng.normal(customer.stochastics["cheese_vars"][0], customer.stochastics["cheese_vars"][1], 1))
    yield env.timeout(t_cheese)

    if customer.flags["print"]:
        print('{:.2f}: {} is served at department C'.format(env.now, customer.ucid))


def cheese_queue(customer, env, cheese_clerks):
    subprocess = env.process(cheese_process(customer, env))
    req_block = env.process(cheese_clerks.request_block(customer, subprocess))
    yield req_block
