import matplotlib.pyplot as plt
import simpy
from simpy import Resource
from operator import itemgetter
import numpy as np
import matplotlib
from simpy.resources.resource import Request, Release


class CustomResource(Resource):
    def __init__(self, env, capacity):
        Resource.__init__(self, env, capacity)
        self.env = env
        self.queueLog = []
        self.capacityLog = []
        self.logs = [self.queueLog, self.capacityLog]

    def requestBlock(self, customer, subprocess):
        req = self.request()

        if customer.flags["print"]:
            print('{:.2f}: {} enters a queue'.format(self.env.now, customer.ucid))

        t0 = self.env.now
        yield req  # wait to be served
        t1 = self.env.now

        if customer.flags["print"]:
            print('{:.2f}: {} is served'.format(self.env.now, customer.ucid))

        if t0 != t1: # if can't be served immediately,  log queue time
            self.queueLog.append(
                {
                    "ucid": customer.ucid,
                    "time": t0,
                    "value": 1
                }
            )

            # queueLog queue exit
            self.queueLog.append(
                {
                    "ucid": customer.ucid,
                    "time": t1,
                    "value": -1
                }
            )

        # log use
        self.capacityLog.append(
            {
                "ucid": customer.ucid,
                "time": t1,
                "value": 1
            }
        )

        yield subprocess

        #log end of use
        self.capacityLog.append(
            {
                "ucid": customer.ucid,
                "time": self.env.now,
                "value": -1
            }
        )
        self.release(req)

    def postprocess_log(self, log):
        time = np.array([el["time"] for el in log])
        entries = np.array([el["value"] for el in log])
        cs = np.cumsum(entries)

        indices = np.where([time[i + 1] == time[i] for i in range(len(time) - 2)])
        cs = np.delete(cs, indices[0])
        time = np.delete(time, indices[0])

        return cs, time
    def plot_use(self):
        fig, ax = plt.subplots()

        currentlyUsed, tUse = self.postprocess_log(self.capacityLog)
        queueLength, tQueue = self.postprocess_log(self.queueLog)

        currentlyAvailable = self.capacity - currentlyUsed
        overflow = -queueLength

        ax.step(tUse, np.append(currentlyAvailable, currentlyAvailable[-1])[:-1], where='post',
                label="Available Resource Count")  # piecewise constant
        ax.step(tQueue, np.append(overflow, overflow[-1])[:-1], where='post',

                label="Overflow (Queue Size)")  # piecewise constant

        ax.set_xlabel("time [s]")
        ax.set_ylabel("resource count")
        ax.legend()

        ax.grid(True)
        plt.show()
        

def createResources(env, n_shoppingcars=45, n_baskets = 300, n_bread=4, n_cheese=3, n_checkouts=4):
    shoppingCarts = CustomResource(env, capacity=n_shoppingcars)
    baskets = CustomResource(env, capacity=n_baskets)
    breadClerks = CustomResource(env, capacity=n_bread)
    cheeseClerks = CustomResource(env, capacity=n_cheese)

    checkouts = [
        CustomResource(env, capacity=1) for _ in range(n_checkouts)
    ]

    # return shoppingCarts, baskets, breadClerks, cheeseClerks, checkouts
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
