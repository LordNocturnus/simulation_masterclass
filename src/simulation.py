import simpy
import json
import matplotlib.pyplot as plt
import numpy as np
import scipy

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
                                                         capacity=self.config["resource quantities"]["shopping_carts"],
                                                         name="Shopping carts")
            resources["baskets"] = TracedResource(env, capacity=self.config["resource quantities"]["baskets"],
                                                  name="Baskets")

            resources["checkout"] = [
                TracedResource(env, capacity=1, name=f"Checkout {i}") for i in range(self.config["resource quantities"]["checkouts"])
            ]
            resources["C"] = departments["C"].queue
            resources["D"] = departments["D"].queue

            # initialize the customer factory, SEED EQUAL TO THE RUN INDEX
            customer_factory = CustomerFactory(env, self.config, departments, resources, seed=run)
            customer_factory.run()

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
        averaged_data = np.mean(interpolated_arrays, axis=0)

        return interpolated_arrays, common_time

    def plot_availability(self, resource, save=False):  # for checkouts, take the first one
        fig, ax = plt.subplots()

        interpolated_availability, time = self.__interporale_availability_to_common_time(resource)

        for run in range(self.runs):
            ax.step(time, np.append(interpolated_availability[run, :], interpolated_availability[run, :][-1])[:-1],
                    where='post',
                    color='k',
                    alpha=0.5,
                    linewidth=0.8
                    )
                    # label="run {}".format(run))  # piecewise constant

        average_availability = interpolated_availability.mean(axis=0)
        std_availability = interpolated_availability.std(axis=0)

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
            plt.savefig("/plots/{}_avaiability.svg".format(resource))
        else:
            plt.show()

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
        awt = np.average(self.wait_times(key))
        aut = np.average(self.use_times(key))
        att = np.average(self.total_times(key))
        print('---------------------------------')
        print(f"use data for {key}")
        print("average queue length: {:.2f}".format(aql))
        print("average wait time [s]: {:.2f}".format(awt))
        print("average use time [s]: {:.2f}".format(aut))
        print("average total time [s]: {:.2f}".format(att))
        print('---------------------------------')

    def print_all_resource_uses(self):
        self.print_use("shopping_carts")
        self.print_use("baskets")
        self.print_use("C")
        self.print_use("D")
        self.print_use("checkout")
