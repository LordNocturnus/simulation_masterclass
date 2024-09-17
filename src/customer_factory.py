from numpy import random as npr
import numpy as np
import json
import sys


from src.customer import Customer


class CustomerFactory:

    def __init__(self, env, customer_config, departments, resources, seed=0):
        self.env = env
        self.rng = npr.default_rng(seed)

        self.departments = departments
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
        t = self.rng.uniform(self.config["arrivals"][hour][0], self.config["arrivals"][hour + 1][0], 1)[0]
        shopping_list = {}
        for dep in self.shopping_list.keys():
            shopping_list[dep] = int(self.rng.choice(self.shopping_list[dep]["items"],
                                                     p=self.shopping_list[dep]["probabilities"]))
        basket = bool(self.rng.binomial(1, self.config["basket"], 10)[0])
        route = self.rng.choice(self.routes, p=self.route_probabilities)
        seed = self.rng.integers(0, sys.maxsize)

        return Customer(self.env, self.config["stochastics"], self.departments, self.resources, self.config["flags"],
                        shopping_list, basket, route, t, ucid, seed)

    def average_wait_time(self):
        n_customers = len(self.customers)
        return {
            "baskets" : sum([customer.wait_times['entrance'] for customer in self.customers if customer.basket]) / n_customers,
            "shopping carts": sum(
                [customer.wait_times['entrance'] for customer in self.customers if not customer.basket]) / n_customers,
            "bread": sum(
                [customer.wait_times['bread'] for customer in self.customers]) / n_customers,
            "cheese": sum(
                [customer.wait_times['cheese'] for customer in self.customers]) / n_customers,
            "checkout": sum(
                [customer.wait_times['checkout'] for customer in self.customers]) / n_customers,

        }

    def wait_times_containers(self):
        """ time customers are waiting for containers"""
        return np.asarray([c.wait_time_container for c in self.customers])

    @property
    def wait_times_baskets(self):
        """ time customers are waiting for baskets"""
        return np.asarray([c.wait_time_container for c in self.customers if c.basket])

    @property
    def wait_times_carts(self):
        """ time customers are waiting for carts"""
        return np.asarray([c.wait_time_container for c in self.customers if not c.basket])

    @property
    def wait_times_checkout(self):
        """ time customers are waiting for a checkout"""
        return np.asarray([c.wait_time_checkout for c in self.customers])

    def wait_times_department(self, department):
        """ time customers are waiting at a specific department"""
        return np.asarray([c.wait_time_department(department) for c in self.customers])

    @property
    def use_times_containers(self):
        """ time customers are in possession of containers"""
        return np.asarray([c.use_time_container for c in self.customers])

    @property
    def use_times_baskets(self):
        """ time customers are in possession of baskets"""
        return np.asarray([c.use_time_container for c in self.customers if c.basket])

    @property
    def use_times_carts(self):
        """ time customers are in possession of carts"""
        return np.asarray([c.use_time_container for c in self.customers if not c.basket])

    @property
    def use_times_checkout(self):
        """ time customers are at a checkout (includes waiting time in checkout queue)"""
        return np.asarray([c.use_time_checkout for c in self.customers])

    def use_times_department(self, department):
        """ time customers are in department (includes waiting time in departments with a queue)"""
        return np.asarray([c.use_time_department(department) for c in self.customers])

    @property
    def active_times_checkout(self):
        """ time customers are using a checkout (does not include waiting time)"""
        return np.asarray([c.active_time_checkout for c in self.customers])

    def active_times_department(self, department):
        """ time customers are in a department getting items (does not include waiting time)"""
        return np.asarray([c.active_time_department(department) for c in self.customers])


