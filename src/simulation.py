import simpy
from src.queuing import createResources
from src.customer_factory import CustomerFactory
import pathlib
import os
import json
import matplotlib.pyplot as plt
import numpy as np


class Simulation:
    """
    Simulation class, used to run the supermarket model
    the class stores simulation results for postprocessing
    """

    def __init__(self, config, runs=1):
        self.runs = runs

        if isinstance(config, dict):
            self.config = config
        else:
            with open(config) as config:  # if it's a path, read the file
                self.config = json.load(config)["Customer"]

        self.resourceLog = []
        self.customerLog = []

    def run(self):
        """
        main function used for running the simulation(s)
        """
        for run in range(self.runs):
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
            self.resourceLog.append(resources)
            self.customerLog.append(customer_factory)

    def average_wait_time(self, resource):  # for checkouts, takes the average over all four
        numerator = 0
        denominator = 0
        for run in range(self.runs):
            if isinstance(self.resourceLog[run][resource],
                          list):  # if it's a list (meaning we're dealing with checkouts)
                for res in self.resourceLog[run][resource]:
                    wait_time = res.waitTimeDictionary()
                    numerator += sum([val for key, val in wait_time.items()])
                    denominator += len(wait_time)
            else:
                wait_time = self.resourceLog[run][resource].waitTimeDictionary()
                numerator += sum([val for key, val in wait_time.items()])
                denominator += len(wait_time)
        return numerator / denominator

    def average_use_time(self, resource):  # for checkouts, takes the average over all four
        numerator = 0
        denominator = 0
        for run in range(self.runs):
            if isinstance(self.resourceLog[run][resource],
                          list):  # if it's a list (meaning we're dealing with checkouts)
                for res in self.resourceLog[run][resource]:
                    use_time = res.useTimeDictionary()
                    numerator += sum([val for key, val in use_time.items()])
                    denominator += len(use_time)
            else:
                use_time = self.resourceLog[run][resource].useTimeDictionary()
                numerator += sum([val for key, val in use_time.items()])
                denominator += len(use_time)
        return numerator / denominator

    def average_queue_length(self, resource):
        numerator = 0
        denominator = 0
        for run in range(self.runs):
            if isinstance(self.resourceLog[run][resource],
                          list):  # if it's a list (meaning we're dealing with checkouts)
                for res in self.resourceLog[run][resource]:
                    queue_length, time = res.postprocess_log(res.queueLog)
                    numerator += sum(queue_length[:-1] * (time[1:] - time[:-1]))
                    denominator += max(time) - min(time)
            else:
                res = self.resourceLog[run][resource]
                queue_length, time = res.postprocess_log(res.queueLog)
                numerator += sum(queue_length[:-1] * (time[1:] - time[:-1]))
                denominator += max(time) - min(time)
        return numerator / denominator

    def plot_availability(self, resource):  # for checkouts, take the first one
        fig, ax = plt.subplots()
        t_max = 0

        for run in range(self.runs):

            if isinstance(self.resourceLog[run][resource], list):
                availability, time = self.resourceLog[run][resource][0].availability()
            else:
                availability, time = self.resourceLog[run][resource].availability()

            t_max = max(t_max, max(time))

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
        ax.set_xlim(0, t_max)

        ax.grid(True)
        plt.show()

    def print_resource_use(self):
        for resource in self.resourceLog[0].keys():
            aql = self.average_queue_length(resource)
            awt = self.average_wait_time(resource)
            aut = self.average_use_time(resource)
            print('---------------------------------')
            print("use data for {}".format(resource))
            print("average queue length: {:.2f}".format(aql))
            print("average wait time [s]: {:.2f}".format(awt))
            print("average use time [s]: {:.2f}".format(aut))
        print('---------------------------------')
