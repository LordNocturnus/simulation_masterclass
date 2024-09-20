import os

import simpy
import json
import matplotlib.pyplot as plt
import numpy as np
import scipy
from scipy.signal import savgol_filter

from src.TracedResource import TracedResource
from src.customer_factory import CustomerFactory
from src.department import Department


class Simulation:
    """
    Simulation class, used to run the supermarket model
    the class stores simulation results for postprocessing
    """

    def __init__(self, config, runs=1, overwrite_print = None):
        self.runs = runs

        if isinstance(config, dict):
            self.config = config
        else:
            with open(config) as config:  # if it's a path, read the file
                self.config = json.load(config)

        if overwrite_print is not None:
            if isinstance(overwrite_print, bool):
                self.config["Customer"]["flags"]["print"] = overwrite_print


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
            resources["shopping carts"] = TracedResource(env,
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

    def store_times(self):
        return np.concatenate([c.store_times for c in self.customerLog])

    def start_times(self):
        return np.concatenate([c.start_times for c in self.customerLog])


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

    def __interporale_availability_to_common_time(self, resource, num_points=1000):

        data_arrays = [None] * self.runs
        time_arrays = [None] * self.runs

        for run in range(self.runs):

            # TODO: figure out how to implement checkouts
            if isinstance(self.resourceLog[run][resource], list):
                availability, time = self.resourceLog[run][resource][0].availability()
            else:
                availability, time = self.resourceLog[run][resource].availability()

            data_arrays[run] = availability
            time_arrays[run] = time

        # Determine the overall time range based on the time arrays
        min_time = max([t.min() for t in time_arrays])  # Max of the min times to avoid extrapolation
        max_time = min([t.max() for t in time_arrays])  # Min of the max times to avoid extrapolation

        common_time = np.linspace(min_time, max_time, num_points)

        interpolated_arrays = []

        # Interpolate each data array to the common time grid
        for time_array, data_array in zip(time_arrays, data_arrays):
            interp_func = scipy.interpolate.interp1d(time_array, data_array, kind='linear', bounds_error=False, fill_value="extrapolate")
            interpolated_data = interp_func(common_time)
            interpolated_arrays.append(interpolated_data)

        # Convert list to numpy array and compute the average along the 0th axis
        interpolated_arrays = np.array(interpolated_arrays)

        return interpolated_arrays, common_time

    def plot_availability(self, resource, save=False, num_points=1000):  # for checkouts, take the first one
        fig, ax = plt.subplots()

        interpolated_availability, time = self.__interporale_availability_to_common_time(resource, num_points=num_points)

        for run in range(self.runs):
            ax.step(time, np.append(interpolated_availability[run, :], interpolated_availability[run, :][-1])[:-1],
                    where='post',
                    color='k',
                    alpha=0.5,
                    linewidth=0.8
                    )

        average_availability = savgol_filter(interpolated_availability.mean(axis=0), window_length=int(num_points/12), polyorder=2)
        std_availability = savgol_filter(interpolated_availability.std(axis=0), window_length=int(num_points/12), polyorder=2)

        # average +- 95% interval
        # TODO: generalize the confidence interval
        ax.plot(time,average_availability, color='r',label='$\mu \pm 2\sigma$')
        ax.plot(time,average_availability-2*std_availability, color='r', linestyle='dashed')
        ax.plot(time,average_availability+2*std_availability, color='r', linestyle='dashed')


        ax.axhline(0, color='k', linestyle='dashed')

        ax.set_xlabel("time [s]")
        ax.set_ylabel("{} availability".format(resource))
        ax.legend()

        ymin, ymax = ax.get_ylim()
        ax.axhspan(ymin=ymin, ymax=0, facecolor='r', alpha=0.25)
        ax.axhspan(ymin=0, ymax=ymax, facecolor='g', alpha=0.25)
        ax.set_ylim(ymin, ymax)
        ax.set_xlim(0, time.max())

        ax.grid(True)
        if save:
            plt.savefig("{}/plots/{}_availability.svg".format(os.getcwd(), resource))
        else:
            plt.show()

        plt.clf()


    def plot_store_time_vs_start_time(self, save=False):
        fig, ax = plt.subplots()
        store_time = self.store_times()
        start_time = self.start_times()

        ax.scatter(start_time, store_time, marker='x')
        ax.axhline(store_time.mean(), color='k', linestyle='dashed')

        ax.set_xlabel("customer arrival time [s]")
        ax.set_ylabel("customer throughput time [s]")

        ax.set_xlim(0, max(start_time))

        ax.grid(True)
        if save:
            plt.savefig("{}/plots/store_time_vs_start_time.svg".format(os.getcwd()))
        else:
            plt.show()

        plt.clf()


    def plot_store_time_histogram(self, save=False, n_bins=50):
        fig, ax = plt.subplots()
        store_time = self.store_times()

        ax.hist(store_time, bins=n_bins)

        mu = store_time.mean()
        sigma = store_time.std()

        # TODO: generalize confidence
        ax.axvline(mu, color='k', label='$\mu \pm 2\sigma$')
        ax.axvline(mu-2*sigma, color='k', linestyle='dashed')
        ax.axvline(mu+2*sigma, color='k', linestyle='dashed')



        ax.set_ylabel("% of customers")
        ax.set_xlabel("customer throughput time [s]")
        ax.legend()

        ax.grid(True)
        if save:
            plt.savefig("{}/plots/store_time_histogram.svg".format(os.getcwd()))
        else:
            plt.show()

        plt.clf()

    def print_basket_use(self):
        aql = self.average_queue_length("baskets")
        wt = self.wait_times_baskets
        ut = self.use_times_baskets
        print('---------------------------------')
        print("use data for baskets")
        print("average queue length: {:.2f}".format(aql))
        print("wait time [s] (min/ave/max): {:.2f}/{:.2f}/{:.2f}".format(wt.min(), wt.mean(), wt.max()))
        print("use time [s] (min/ave/max): {:.2f}/{:.2f}/{:.2f}".format(ut.min(), ut.mean(), ut.max()))
        print('---------------------------------')

    def print_cart_use(self):
        aql = self.average_queue_length("shopping carts")
        wt = self.wait_times_carts
        ut = self.use_times_carts
        print('---------------------------------')
        print("use data for shopping carts")
        print("average queue length: {:.2f}".format(aql))
        print("wait time [s] (min/ave/max): {:.2f}/{:.2f}/{:.2f}".format(wt.min(), wt.mean(), wt.max()))
        print("use time [s] (min/ave/max): {:.2f}/{:.2f}/{:.2f}".format(ut.min(), ut.mean(), ut.max()))
        print('---------------------------------')

    def print_checkout_use(self):
        aql = self.average_queue_length("checkouts")
        wt = self.wait_times_checkout
        ut = self.use_times_checkout
        at = self.active_times_checkout
        print('---------------------------------')
        print("use data for checkouts")
        print("average queue length: {:.2f}".format(aql))
        print("wait time [s] (min/ave/max): {:.2f}/{:.2f}/{:.2f}".format(wt.min(), wt.mean(), wt.max()))
        print("use time [s] (min/ave/max): {:.2f}/{:.2f}/{:.2f}".format(ut.min(), ut.mean(), ut.max()))
        print("active time [s] (min/ave/max): {:.2f}/{:.2f}/{:.2f}".format(at.min(), at.mean(), at.max()))
        print('---------------------------------')

    def print_cheese_use(self):
        aql = self.average_queue_length("cheese")
        wt = self.wait_times_department("D")
        ut = self.use_times_department("D")
        at = self.active_times_department("D")
        print('---------------------------------')
        print("use data for cheese")
        print("average queue length: {:.2f}".format(aql))
        print("wait time [s] (min/ave/max): {:.2f}/{:.2f}/{:.2f}".format(wt.min(), wt.mean(), wt.max()))
        print("use time [s] (min/ave/max): {:.2f}/{:.2f}/{:.2f}".format(ut.min(), ut.mean(), ut.max()))
        print("active time [s] (min/ave/max): {:.2f}/{:.2f}/{:.2f}".format(at.min(), at.mean(), at.max()))
        print('---------------------------------')

    def print_bread_use(self):
        aql = self.average_queue_length("bread")
        wt = self.wait_times_department("C")
        ut = self.use_times_department("C")
        at = self.active_times_department("C")
        print('---------------------------------')
        print("use data for bread")
        print("average queue length: {:.2f}".format(aql))
        print("wait time [s] (min/ave/max): {:.2f}/{:.2f}/{:.2f}".format(wt.min(), wt.mean(), wt.max()))
        print("use time [s] (min/ave/max): {:.2f}/{:.2f}/{:.2f}".format(ut.min(), ut.mean(), ut.max()))
        print("active time [s] (min/ave/max): {:.2f}/{:.2f}/{:.2f}".format(at.min(), at.mean(), at.max()))
        print('---------------------------------')

    def print_all_resource_uses(self):
        self.print_cart_use()
        self.print_basket_use()
        self.print_bread_use()
        self.print_cheese_use()
        self.print_checkout_use()

    def print_store_time(self):
        store_times = self.store_times()
        print('---------------------------------')
        print("store time [s] (min/ave/max): {:.2f}/{:.2f}/{:.2f}".format(store_times.min(), store_times.mean(), store_times.max()))
        sigma = store_times.std()
        print('95% confidence interval: {:.2f} - {:.2f} [s]'.format(
            store_times.mean() - 2 * sigma, store_times.mean() + 2 * sigma
        ))
        print('---------------------------------')


