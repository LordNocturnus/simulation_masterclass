import simpy
from src.queuing import createResources
from src.customer_factory import CustomerFactory
import pathlib
import os
import matplotlib.pyplot as plt
import numpy as np
class MultiSim():
    def __init__(self, N_RUNS):
        self.N_RUNS = N_RUNS
        self.resource_use_log = [None] * self.N_RUNS


    def run(self):
        for run in range(self.N_RUNS):
            env = simpy.Environment()

            # initialize shared resources
            resources = createResources(env, n_shoppingcars=45, n_baskets=300, n_bread=4, n_cheese=3, n_checkouts=4)

            print(pathlib.Path(os.getcwd()).joinpath("config.json"))
            customer_factory = CustomerFactory(env, pathlib.Path(os.getcwd()).joinpath("config.json"), resources, seed=run)
            customer_factory.run()

            env.run()

            self.resource_use_log[run] = resources

    def averageWaitTime(self, resource):  # for checkouts, takes the average over all four
        numerator = 0
        denominator = 0
        for run in range(self.N_RUNS):
            if isinstance(self.resource_use_log[run][resource], list):
                for res in self.resource_use_log[run][resource]:
                    dict = res.waitTimeDictionary()
                    numerator += sum([val for key, val in dict.items()])
                    denominator += len(dict)
            else:
                dict = self.resource_use_log[run][resource].waitTimeDictionary()
                numerator += sum([val for key, val in dict.items()])
                denominator += len(dict)
        return numerator / denominator


    def plotAvailability(self, resource):
        fig, ax = plt.subplots()

        for run in range(self.N_RUNS):

            availability, time = self.resource_use_log[run][resource].availability()

            ax.step(time, np.append(availability, availability[-1])[:-1], where='post', label="run {}".format(run))  # piecewise constant

        ax.axhline(0, color='k', linestyle='dashed')

        ax.set_xlabel("time [s]")
        ax.set_ylabel("resource count")
        ax.legend()

        ax.grid(True)
        plt.show()