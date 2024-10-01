import os

import simpy
import json
import matplotlib.pyplot as plt
import numpy as np
import scipy
from scipy.signal import savgol_filter

from src.TracedResource import TracedResource
from src.customer_factory import CustomerFactory
from src.customer_visualization import Visualization
from src.store import Store
from src.plotting import plot_average


class Simulation:
    """
    Simulation class, used to run the supermarket model
    the class stores simulation results for postprocessing
    """

    def __init__(self, config, runs=1, overwrite_print = None, visualization=False):
        self.runs = runs

        if isinstance(config, dict):
            self.config = config
        else:
            with open(config) as config:  # if it's a path, read the file
                self.config = json.load(config)

        if overwrite_print is not None:
            if isinstance(overwrite_print, bool):
                self.config["Customer"]["flags"]["print"] = overwrite_print

        self.visualization = visualization


        self.resourceLog = []
        self.customerLog = []
        self.departmentLog = []

    def run(self):
        """
        main function used for running the simulation(s)
        """
        for run in range(self.runs):
            env = simpy.Environment()

            store = Store(env, self.config)
            store.plot()

            # initialize shared resources
            resources = dict()
            resources["shopping_carts"] = TracedResource(env,
                                                         capacity=self.config["resource quantities"]["shopping_carts"],
                                                         name="Shopping carts")
            resources["baskets"] = TracedResource(env, capacity=self.config["resource quantities"]["baskets"],
                                                  name="Baskets")

            resources["checkout"] = [
                TracedResource(env, capacity=1, name=f"Checkout {i}") for i in range(self.config["resource quantities"]["checkouts"])
            ]
            resources["C"] = store.departments["C"].queue
            resources["D"] = store.departments["D"].queue

            self.departmentLog.append(store.departments)

            # initialize the customer factory, SEED EQUAL TO THE RUN INDEX
            customer_factory = CustomerFactory(env, self.config, store, resources, seed=run)
            customer_factory.run()

            if self.visualization:
                visualization = Visualization(store, customer_factory, env, np.asarray([40.0, 30.0]))
                env.process(visualization.run(env))

            # run simulation
            env.run()
            print(f"finished run {run}")

            # store results
            self.resourceLog.append(resources)
            self.customerLog.append(customer_factory)

    def wait_times(self, key):
        return np.concatenate([r.wait_times(key) for r in self.customerLog])

    def use_times(self, key):
        return np.concatenate([r.use_times(key) for r in self.customerLog])

    def total_times(self, key):
        return np.concatenate([r.total_times(key) for r in self.customerLog])

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
    def plot_availability_v2(self, key, confidence=True, individual=False, save=False):
        data = []

        for run in range(self.runs):
            availability, time = self.resourceLog[run][key].availability()
            availability = np.insert(availability, 0, self.config["resource quantities"][key])
            time = np.insert(time, 0, 0)
            data.append(np.asarray([time, availability]))

        plot_average(data, "Time [s]", f"Available {key} [-]",
                     "Average Baskets available over time", confidence, individual, save)

    def print_use(self, key):
        aql = self.average_queue_length(key)
        wt = self.wait_times(key)
        ut = self.use_times(key)
        tt = self.total_times(key)
        print('---------------------------------')
        print(f"use data for {key}")
        print("average queue length: {:.2f}".format(aql))
        print("wait time [s] (min/ave/max): {:.2f}/{:.2f}/{:.2f}".format(wt.min(), wt.mean(), wt.max()))
        print("use time [s] (min/ave/max): {:.2f}/{:.2f}/{:.2f}".format(ut.min(), ut.mean(), ut.max()))
        print("total time [s] (min/ave/max): {:.2f}/{:.2f}/{:.2f}".format(tt.min(), tt.mean(), tt.max()))
        print('---------------------------------')

    def print_all_resource_uses(self):
        self.print_use("shopping_carts")
        self.print_use("baskets")
        self.print_use("C")
        self.print_use("D")
        self.print_use("checkout")

    def print_store_time(self):
        store_times = self.store_times()
        print('---------------------------------')
        print("store time [s] (min/ave/max): {:.2f}/{:.2f}/{:.2f}".format(store_times.min(), store_times.mean(), store_times.max()))
        sigma = store_times.std()
        print('95% confidence interval: {:.2f} - {:.2f} [s]'.format(
            store_times.mean() - 2 * sigma, store_times.mean() + 2 * sigma
        ))
        print('---------------------------------')


