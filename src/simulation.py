import simpy
from src.queuing import createResources
from src.customer_factory import CustomerFactory
import pathlib
import os
import json
import matplotlib.pyplot as plt
import numpy as np
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
            env = simpy.Environment()

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
            self.customerLog[run] = customer_factory

    def averageWaitTime(self, resource):  # for checkouts, takes the average over all four
        numerator = 0
        denominator = 0
        for run in range(self.N_RUNS):
            if isinstance(self.resourceLog[run][resource], list): # if it's a list (meaning we're dealing with checkouts)
                for res in self.resourceLog[run][resource]:
                    dict = res.waitTimeDictionary()
                    numerator += sum([val for key, val in dict.items()])
                    denominator += len(dict)
            else:
                dict = self.resourceLog[run][resource].waitTimeDictionary()
                numerator += sum([val for key, val in dict.items()])
                denominator += len(dict)
        return numerator / denominator

    def averageUseTime(self, resource):  # for checkouts, takes the average over all four
        numerator = 0
        denominator = 0
        for run in range(self.N_RUNS):
            if isinstance(self.resourceLog[run][resource], list): # if it's a list (meaning we're dealing with checkouts)
                for res in self.resourceLog[run][resource]:
                    dict = res.useTimeDictionary()
                    numerator += sum([val for key, val in dict.items()])
                    denominator += len(dict)
            else:
                dict = self.resourceLog[run][resource].useTimeDictionary()
                numerator += sum([val for key, val in dict.items()])
                denominator += len(dict)
        return numerator / denominator

    def averageQueueLength(self, resource):
        numerator = 0
        denominator = 0
        for run in range(self.N_RUNS):
            if isinstance(self.resourceLog[run][resource],
                          list):  # if it's a list (meaning we're dealing with checkouts)
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

    def printResourceUse(self):
        for resource in self.resourceLog[0].keys():
            aql = self.averageQueueLength(resource)
            awt = self.averageWaitTime(resource)
            aut = self.averageUseTime(resource)
            print('---------------------------------')
            print("use data for {}".format(resource))
            print("average queue length: {:.2f}".format(aql))
            print("average wait time [s]: {:.2f}".format(awt))
            print("average use time [s]: {:.2f}".format(aut))
        print('---------------------------------')

