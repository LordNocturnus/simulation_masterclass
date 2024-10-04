from numpy import random as npr
import numpy as np
import json
import sys


from src.customer import Customer


class CustomerFactory:

    def __init__(self, env, customer_config, store, resources, seed=0):
        self.env = env
        self.rng = npr.default_rng(seed)

        self.store = store
        self.resources = resources

        self.customers = []

        # customer_config can be either a path or a dictionary
        if isinstance(customer_config, dict):
            self.config = customer_config["Customer"] # only load the customer  section
        else:
            with open(customer_config) as config: # if it's a path, read the file
                self.config = json.load(config)["Customer"]

        self.shopping_list = {}
        for dep in self.config["items"].keys():
            self.shopping_list[dep] = {}
            # create a triangular probability function for items
            self.shopping_list[dep]["items"] = np.arange(self.config["items"][dep][0], self.config["items"][dep][2] + 1, 1)
            self.shopping_list[dep]["probabilities"] = np.interp(self.shopping_list[dep]["items"],
                                                                 [self.config["items"][dep][0] - 0.5,
                                                                self.config["items"][dep][1],
                                                                self.config["items"][dep][2] + 0.5],
                                                                 [0.0, 2 / (self.config["items"][dep][2] -
                                                                          self.config["items"][dep][0] + 1), 0.0])
            # correct for slight errors in interploation to ensure P(omega)=1
            self.shopping_list[dep]["probabilities"] /= np.sum(self.shopping_list[dep]["probabilities"])

        self.routes = []
        self.route_probabilities = []
        for route in self.config["route"].keys():
            self.routes.append(route)
            self.route_probabilities.append(self.config["route"][route])

    def run(self):
        ucid = 0
        for k, v in enumerate(self.config["arrivals"][:-1]):
            count = self.rng.poisson(v[1])
            for _ in range(count):
                self.customers.append(self.create_customer(k, ucid))
                ucid +=1

    def create_customer(self, hour, ucid) -> Customer:
        t = self.rng.uniform(self.config["arrivals"][hour][0], self.config["arrivals"][hour + 1][0])
        shopping_list = {}
        for dep in self.shopping_list.keys():
            shopping_list[dep] = int(self.rng.choice(self.shopping_list[dep]["items"],
                                                     p=self.shopping_list[dep]["probabilities"]))
        basket = bool(self.rng.binomial(1, self.config["basket"]))
        route = self.rng.choice(self.routes, p=self.route_probabilities)
        seed = self.rng.integers(0, sys.maxsize)

        if basket:
            walking_speed = self.rng.uniform(self.config["stochastics"]["walking_basket"][0],
                                             self.config["stochastics"]["walking_basket"][1]) / 3.6 # convert km/h to m/s
        else:
            walking_speed = self.rng.triangular(self.config["stochastics"]["walking_cart"][0],
                                                self.config["stochastics"]["walking_cart"][1],
                                                self.config["stochastics"]["walking_cart"][2],) / 3.6

        return Customer(self.env, self.config["stochastics"], self.store, self.resources, self.config["flags"],
                        shopping_list, basket, route, t, walking_speed, self.config["size"], ucid, seed)

    def wait_times(self, key):
        if key == "baskets":
            return np.asarray([c.wait_times["container"] for c in self.customers if c.basket])
        elif key == "shopping_carts":
            return np.asarray([c.wait_times["container"] for c in self.customers if not c.basket and "container" in c.wait_times.keys()])
        return np.asarray([c.wait_times[key] for c in self.customers if key in c.wait_times.keys()])

    def use_times(self, key):
        if key == "baskets":
            return np.asarray([c.use_times["container"] for c in self.customers if c.basket])
        elif key == "shopping_carts":
            return np.asarray([c.use_times["container"] for c in self.customers if not c.basket and "container" in c.use_times.keys()])
        return np.asarray([c.use_times[key] for c in self.customers if key in c.use_times.keys()])

    def total_times(self, key):
        if key == "baskets":
            return np.asarray([c.total_time("container") for c in self.customers if c.basket])
        elif key == "shopping_carts":
            return np.asarray([c.total_time("container") for c in self.customers if not c.basket and "container" in c.use_times.keys() and "container" in c.wait_times.keys()])
        return np.asarray([c.total_time(key) for c in self.customers if key in c.use_times.keys() and key in c.wait_times.keys()])

    @property
    def store_times(self):
        """ time spent in the store """
        return np.asarray([c.store_time for c in self.customers])

    @property
    def start_times(self):
        return np.asarray([c.start_time for c in self.customers])

    @property
    def simulation_end_time(self):
        # total simulation runs from zero until the last customer leaves the store
        return max([c.exit_time for c in self.customers])



