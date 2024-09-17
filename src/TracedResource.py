import matplotlib.pyplot as plt
import simpy
from simpy import Resource
from operator import itemgetter
import numpy as np
import matplotlib
from simpy.resources.resource import Request, Release


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

    def requestBlock(self, customer, subprocess):
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
                "value":-1
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

    def plotAvailability(self):
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

    def getWaitTime(self, ucid : int):
        timestamps = [logEntry["time"] for logEntry in self.queueLog if logEntry["ucid"] == ucid]
        if timestamps:
            return timestamps[-1] - timestamps[0]
        else:
            return 0

    def getUseTime(self, ucid: int):
        timestamps = [logEntry["time"] for logEntry in self.capacityLog if logEntry["ucid"] == ucid]
        return timestamps[-1] - timestamps[0]

    def waitTimeDictionary(self):
        dict = {}
        for ucid in self.ucids:
            dict[str(ucid)] = self.getWaitTime(ucid)

        return dict

    def useTimeDictionary(self):
        dict = {}
        for ucid in self.ucids:
            dict[str(ucid)] = self.getUseTime(ucid)

        return dict

    def averageWaitTime(self):
        dict = self.waitTimeDictionary()
        ave = sum([val for key, val in dict.items()]) / len(dict)
        return ave

    def averageUseTime(self):
        dict = self.useTimeDictionary()
        ave = sum([val for key, val in dict.items()]) / len(dict)
        return ave
    def waitTimeHistogram(self):

        fig, ax = plt.subplots()
        data = self.waitTimeDictionary()

        ax.hist(data.values(), bins=25)

        ax.set_ylabel("no. of {} users".format(self.name))
        ax.set_xlabel("wait time [s]")
        ax.legend()

        ax.grid(True)
        plt.show()

    def useTimeHistogram(self):

        fig, ax = plt.subplots()
        data = self.useTimeDictionary()

        ax.hist(data.values(), bins=25)

        ax.set_ylabel("no. of {} users".format(self.name))
        ax.set_xlabel("use time [s]")
        ax.legend()

        ax.grid(True)
        plt.show()

def createResources(env, n_shoppingcars=45, n_baskets = 300, n_bread=4, n_cheese=3, n_checkouts=4):
    shoppingCarts = TracedResource(env, capacity=n_shoppingcars, name="shopping carts")
    baskets = TracedResource(env, capacity=n_baskets, name="baskets")
    breadClerks = TracedResource(env, capacity=n_bread, name='bread clerks')
    cheeseClerks = TracedResource(env, capacity=n_cheese, name ='cheese clerks')

    checkouts = [
        TracedResource(env, capacity=1, name = "checkout") for _ in range(n_checkouts)
    ]

    return {
        "shopping carts" : shoppingCarts,
        "baskets" : baskets,
        "bread clerks" : breadClerks,
        "cheese clerks" : cheeseClerks,
        "checkouts" : checkouts
    }


def checkoutProcess(customer, env):
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

def checkoutQueues(customer, env, checkouts):

    #access checkout queues to see which is the quickest
    queue_lengths = [
        len(ch.put_queue) + ch.count for ch in checkouts
    ]

    # find the index of the shortest queue
    index, element = min(enumerate(queue_lengths), key=itemgetter(1))

    # enter the shortest queue
    subprocess = env.process(checkoutProcess(customer, env))
    reqBlock = env.process(checkouts[index].requestBlock(customer, subprocess))
    yield reqBlock


def breadProcess(customer, env):
    t_bread = float(
        customer.rng.normal(customer.stochastics["bread_vars"][0], customer.stochastics["bread_vars"][1], 1))
    yield env.timeout(t_bread)

    if customer.flags["print"]:
        print('{:.2f}: {} is served at department C'.format(env.now, customer.ucid))

def breadQueue(customer, env, breadClerks):

    subprocess = env.process(breadProcess(customer, env))
    reqBlock = env.process(breadClerks.requestBlock(customer, subprocess))
    yield reqBlock

def cheeseProcess(customer, env):
    t_cheese = float(customer.rng.normal(customer.stochastics["cheese_vars"][0], customer.stochastics["cheese_vars"][1], 1))
    yield env.timeout(t_cheese)

    if customer.flags["print"]:
        print('{:.2f}: {} is served at department C'.format(env.now, customer.ucid))

def cheeseQueue(customer, env, cheeseClerks):
    subprocess = env.process(cheeseProcess(customer, env))
    reqBlock = env.process(cheeseClerks.requestBlock(customer, subprocess))
    yield reqBlock
