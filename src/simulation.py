import simpy
import json
import matplotlib.pyplot as plt
import numpy as np


from src.TracedResource import TracedResource
from src.customer_factory import CustomerFactory
from src.department import Department
from src.plotting import plot_average


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
                self.config = json.load(config)

        self.resourceLog = []
        self.customerLog = []

    def run(self):
        """
        main function used for running the simulation(s)
        """
        for run in range(self.runs):
            env = simpy.Environment()

            departments = dict()
            departments["A"] = Department("A - Fruit & Vegetables", env)
            departments["B"] = Department("B - Meat & Fish", env)
            departments["C"] = Department("C - Bread", env, self.config["resource quantities"]["bread clerks"],
                                          self.config["Customer"]["stochastics"]["bread_vars"])
            departments["D"] = Department("D - Cheese", env, self.config["resource quantities"]["cheese clerks"],
                                          self.config["Customer"]["stochastics"]["cheese_vars"])
            departments["E"] = Department("E - Canned & packed food", env)
            departments["F"] = Department("F - Frozen food", env)
            departments["G"] = Department("G - Drinks", env)

            # initialize shared resources
            resources = dict()
            resources["shopping_carts"] = TracedResource(env,
                                                         capacity=self.config["resource quantities"]["shopping carts"],
                                                         name="Shopping carts")
            resources["baskets"] = TracedResource(env, capacity=self.config["resource quantities"]["baskets"],
                                                  name="Baskets")

            resources["checkouts"] = [
                TracedResource(env, capacity=1, name=f"Checkout {i}") for i in range(self.config["resource quantities"]["checkouts"])
            ]
            resources["bread"] = departments["C"].queue
            resources["cheese"] = departments["D"].queue

            # initialize the customer factory, SEED EQUAL TO THE RUN INDEX
            customer_factory = CustomerFactory(env, self.config, departments, resources, seed=run)
            customer_factory.run()

            # run simulation
            env.run()
            print(f"finished run {run}")

            # store results
            self.resourceLog.append(resources)
            self.customerLog.append(customer_factory)

    @property
    def wait_times_containers(self):
        """ time customers are waiting for containers"""
        return np.concatenate([r.wait_times_containers for r in self.customerLog])

    @property
    def wait_times_baskets(self):
        """ time customers are waiting for baskets"""
        return np.concatenate([c.wait_times_baskets for c in self.customerLog])

    @property
    def wait_times_carts(self):
        """ time customers are waiting for carts"""
        return np.concatenate([c.wait_times_carts for c in self.customerLog])

    @property
    def wait_times_checkout(self):
        """ time customers are waiting for a checkout"""
        return np.concatenate([c.wait_times_checkout for c in self.customerLog])

    def wait_times_department(self, department):
        """ time customers are waiting at a specific department"""
        return np.concatenate([c.wait_times_department(department) for c in self.customerLog])

    @property
    def use_times_containers(self):
        """ time customers are in possession of containers"""
        return np.concatenate([c.use_times_containers for c in self.customerLog])

    @property
    def use_times_baskets(self):
        """ time customers are in possession of baskets"""
        return np.concatenate([c.use_times_baskets for c in self.customerLog])

    @property
    def use_times_carts(self):
        """ time customers are in possession of carts"""
        return np.concatenate([c.use_times_carts for c in self.customerLog])

    @property
    def use_times_checkout(self):
        """ time customers are at a checkout (includes waiting time in checkout queue)"""
        return np.concatenate([c.use_times_checkout for c in self.customerLog])

    def use_times_department(self, department):
        """ time customers are in department (includes waiting time in departments with a queue)"""
        return np.concatenate([c.use_times_department(department) for c in self.customerLog])

    @property
    def active_times_checkout(self):
        """ time customers are using a checkout (does not include waiting time)"""
        return np.concatenate([c.active_times_checkout for c in self.customerLog])

    def active_times_department(self, department):
        """ time customers are in a department getting items (does not include waiting time)"""
        return np.concatenate([c.active_times_department(department) for c in self.customerLog])

    def average_queue_length(self, resource):
        numerator = 0
        denominator = 0
        for run in range(self.runs):
            if isinstance(self.resourceLog[run][resource],
                          list):  # if it's a list (meaning we're dealing with checkouts)
                for res in self.resourceLog[run][resource]:
                    queue_length, time = res.queue_length()
                    numerator += np.sum(queue_length[:-1] * np.diff(time))
                    denominator += max(time)
            else:
                res = self.resourceLog[run][resource]
                queue_length, time = res.queue_length()
                numerator += np.sum(queue_length[:-1] * np.diff(time))
                denominator += max(time)
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

        plt.show()

    def plot_basket_availability(self, confidence=True):
        data = []

        for run in range(self.runs):
            availability, time = self.resourceLog[run]["baskets"].availability()
            availability = np.insert(availability, 0, self.config["resource quantities"]["baskets"])
            time = np.insert(time, 0, 0)
            data.append(np.asarray([time, availability]))

        plot_average(data, "Time [s]", "Available Baskets [-]",
                     "Average Baskets available over time", confidence)

    def plot_cart_availability(self, confidence=True):
        data = []

        for run in range(self.runs):
            availability, time = self.resourceLog[run]["shopping_carts"].availability()
            availability = np.insert(availability, 0, self.config["resource quantities"]["shopping carts"])
            time = np.insert(time, 0, 0)
            data.append(np.asarray([time, availability]))

        plot_average(data, "Time [s]", "Available Shopping Carts [-]",
                     "Average Shopping Carts available over time", confidence)


    def print_basket_use(self):
        aql = self.average_queue_length("baskets")
        awt = np.average(self.wait_times_baskets)
        aut = np.average(self.use_times_baskets)
        print('---------------------------------')
        print("use data for Baskets")
        print("average queue length: {:.2f}".format(aql))
        print("average wait time [s]: {:.2f}".format(awt))
        print("average use time [s]: {:.2f}".format(aut))
        print('---------------------------------')

    def print_cart_use(self):
        aql = self.average_queue_length("shopping_carts")
        awt = np.average(self.wait_times_carts)
        aut = np.average(self.use_times_carts)
        print('---------------------------------')
        print("use data for Carts")
        print("average queue length: {:.2f}".format(aql))
        print("average wait time [s]: {:.2f}".format(awt))
        print("average use time [s]: {:.2f}".format(aut))
        print('---------------------------------')

    def print_checkout_use(self):
        aql = self.average_queue_length("checkouts")
        awt = np.average(self.wait_times_checkout)
        aut = np.average(self.use_times_checkout)
        aat = np.average(self.active_times_checkout)
        print('---------------------------------')
        print("use data for Checkouts")
        print("average queue length: {:.2f}".format(aql))
        print("average wait time [s]: {:.2f}".format(awt))
        print("average use time [s]: {:.2f}".format(aut))
        print("average active time [s]: {:.2f}".format(aat))
        print('---------------------------------')

    def print_cheese_use(self):
        aql = self.average_queue_length("bread")
        awt = np.average(self.wait_times_department("C"))
        aut = np.average(self.use_times_department("C"))
        aat = np.average(self.active_times_department("C"))
        print('---------------------------------')
        print("use data for Bread")
        print("average queue length: {:.2f}".format(aql))
        print("average wait time [s]: {:.2f}".format(awt))
        print("average use time [s]: {:.2f}".format(aut))
        print("average active time [s]: {:.2f}".format(aat))
        print('---------------------------------')

    def print_bread_use(self):
        aql = self.average_queue_length("cheese")
        awt = np.average(self.wait_times_department("D"))
        aut = np.average(self.use_times_department("D"))
        aat = np.average(self.active_times_department("D"))
        print('---------------------------------')
        print("use data for Cheese")
        print("average queue length: {:.2f}".format(aql))
        print("average wait time [s]: {:.2f}".format(awt))
        print("average use time [s]: {:.2f}".format(aut))
        print("average active time [s]: {:.2f}".format(aat))
        print('---------------------------------')