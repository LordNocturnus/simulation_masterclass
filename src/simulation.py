import simpy
from src.queuing import createResources
from src.customer_factory import CustomerFactory
import pathlib
import os
import json
import matplotlib.pyplot as plt
import numpy as np
import copy
class Simulation():
    """
    Simulation class, used to run the supermarket model
    the class stores simulation results for postprocessing
    """
    def __init__(self, config, N_RUNS=1):
        self.N_RUNS = N_RUNS

        if isinstance(config, dict):
            self.config = config
        else:
            with open(config) as config: # if it's a path, read the file
                self.config = json.load(config)["Customer"]
        self.config = config
        self.resourceLog = [None] * N_RUNS
        self.customerLog = [None] * N_RUNS

    def run(self):
        """
        main function used for running the simulation(s)
        """
        for run in range(self.N_RUNS):
            env = simpy.Environment(0.0)

            # initialize shared resources
            resources = createResources(env, n_shoppingcars=self.config["resource quantities"]["shopping carts"],
                                        n_baskets=self.config["resource quantities"]["baskets"],
                                        n_bread=self.config["resource quantities"]["bread clerks"],
                                        n_cheese=self.config["resource quantities"]["cheese clerks"],
                                        n_checkouts=self.config["resource quantities"]["checkouts"])

            # initialize the customer factory, SEED EQUAL TO THE RUN INDEX
            customer_factory = CustomerFactory(env, self.config, resources, seed=run)
            customer_factory.run()

            # run simulation
            env.run()

            # store results
            self.resourceLog[run] = resources
            self.customerLog[run] = customer_factory.customers

    def waitTimeData(self, resource):  # for checkouts, takes the average over all four
        waitTime = np.array([])
        arrivalTime = np.array([])

        for run in range(self.N_RUNS):
            customers = self.customerLog[run]

            wt = np.array([c.wait_times[resource] for c in customers if resource in c.wait_times])
            at = np.array([c.arrival_times[resource] for c in customers if resource in c.wait_times])

            waitTime = np.append(waitTime, wt)
            arrivalTime = np.append(arrivalTime, at)

        return waitTime, arrivalTime
    def useTimeData(self, resource):  # for checkouts, takes the average over all four
        useTime = np.array([])
        arrivalTime = np.array([])

        for run in range(self.N_RUNS):
            customers = self.customerLog[run]

            # wt = np.array([c.use_times[resource] for c in customers if resource in c.use_times])
            # at = np.array([c.start_time for c in customers if resource in c.use_times])

            ut = np.array([c.use_times[resource] for c in customers if resource in c.use_times])
            at = np.array([c.arrival_times[resource] for c in customers if resource in c.use_times])

            useTime = np.append(useTime, ut)
            arrivalTime = np.append(arrivalTime, at)

        return useTime, arrivalTime

    def averageQueueLength(self, resource):
        numerator = 0
        denominator = 0
        for run in range(self.N_RUNS):
            if isinstance(self.resourceLog[run][resource], list):  # if it's a list (meaning we're dealing with checkouts)
                for res in self.resourceLog[run][resource]:
                    queueLength, time = res.postprocess_log(res.queueLog)
                    numerator += sum(queueLength[:-1] * (time[1:] - time[:-1]))
                    denominator += max(time) - min(time)
            else:
                res = self.resourceLog[run][resource]
                queueLength, time = res.postprocess_log(res.queueLog)
                numerator += sum(queueLength[:-1] * (time[1:] - time[:-1]))
                denominator += max(time) - min(time)
        return numerator / denominator


    def plotAvailability(self, resource): # for checkouts, take the first one
        fig, ax = plt.subplots()

        for run in range(self.N_RUNS):

            if isinstance(self.resourceLog[run][resource], list):
                availability, time = self.resourceLog[run][resource][0].availability()
            else:
                availability, time = self.resourceLog[run][resource].availability()

            ax.step(time, np.append(availability, availability[-1])[:-1],
                    where='post', label="run {}".format(run))  # piecewise constant

        ax.axhline(0, color='k', linestyle='dashed')

        ax.set_xlabel("time [s]")
        ax.set_ylabel("{} availability".format(resource))
        ax.legend()

        ymin, ymax = ax.get_ylim()
        ax.axhspan(ymin=ymin, ymax=0, facecolor='r', alpha=0.25)
        ax.axhspan(ymin=0, ymax=ymax, facecolor='g', alpha=0.25)
        ax.set_ylim(ymin, ymax)
        ax.set_xlim(0, max(time))


        ax.grid(True)
        plt.show()

    def customerThroughputData(self):
        throughputTime = np.array([])
        arrivalTime = np.array([])
        for run in range(self.N_RUNS):
            customers = self.customerLog[run]

            # total time in the store is the wait time + use time of basket or cart
            tt = np.array([c.wait_times["baskets"] + c.use_times["baskets"] if c.basket else
            c.wait_times["shopping carts"] + c.use_times["shopping carts"] for c in customers])
            at = np.array([c.start_time for c in customers])

            throughputTime = np.append(throughputTime, tt)
            arrivalTime = np.append(arrivalTime, at)

        return throughputTime, arrivalTime

    def printThroughputData(self):
        tt, at = self.customerThroughputData()
        print('Customer throughput time [s] (min/ave/max): {:.2f}/{:.2f}/{:.2f}'.format(
            tt.min(), tt.mean(), tt.max()
        ))
        sigma = tt.std()
        print('95% confidence interval: {:.2f} - {:.2f} [s]'.format(
            tt.mean() - 2 * sigma, tt.mean() + 2*sigma
        ))


    def plotThroughputVsArrivalTime(self):
        fig, ax = plt.subplots()
        tt, at = self.customerThroughputData()

        ax.scatter(at, tt, marker='x')
        ax.axhline(tt.mean(), color='k', linestyle='dashed')

        ax.set_xlabel("customer arrival time [s]")
        ax.set_ylabel("customer throughput time [s]")

        ax.set_xlim(0, max(at))

        ax.grid(True)
        plt.show()

    def plotThroughputHistogram(self):
        fig, ax = plt.subplots()
        tt, at = self.customerThroughputData()

        ax.hist(tt, bins=50)

        ax.set_xlabel("no. of customers [s]")
        ax.set_ylabel("customer throughput time [s]")

        ax.grid(True)
        plt.show()

    def plotUseHistogram(self, resource):
        fig, ax = plt.subplots()
        tt, at = self.useTimeData(resource)

        ax.hist(tt, bins=50)

        ax.set_xlabel("no. of customers [s]")
        ax.set_ylabel("{} use time [s]".format(resource))

        ax.grid(True)
        plt.show()


    def plotWaitTime(self, resource):
        pass


    def printResourceUse(self):
        for resource in self.resourceLog[0].keys():
            aql = self.averageQueueLength(resource)
            wt, at = self.waitTimeData(resource)
            ut, at = self.useTimeData(resource)
            print('---------------------------------')
            print("use data for {}".format(resource))
            print("average queue length: {:.2f}".format(aql))
            print("wait time [s] (min/ave/max): {:.2f}/{:.2f}/{:.2f}".format(wt.min(), wt.mean(), wt.max()))
            print("use time [s] (min/ave/max): {:.2f}/{:.2f}/{:.2f}".format(ut.min(), ut.mean(), ut.max()))
        print('---------------------------------')

