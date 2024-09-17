from numpy import random as npr
import numpy as np
import json
import sys


from src.customer import Customer


class CustomerFactory:

    def __init__(self, env, customer_config, resources, seed=0):
        self.env = env
        self.customers = []
        self.rng = npr.default_rng(seed)
        self.resources = resources

        # customer_config can be either a path or a dictionary
        if isinstance(customer_config, dict):
            self.config = customer_config["Customer"] # only load the customer  section
        else:
            with open(customer_config) as config: # if it's a path, read the file
                self.config = json.load(config)["Customer"]

        self.departments = {}
        for dep in self.config["items"].keys():
            self.departments[dep] = {}
            # create a triangular probability function for items
            self.departments[dep]["items"] = np.arange(self.config["items"][dep][0], self.config["items"][dep][2] + 1, 1)
            self.departments[dep]["probabilities"] = np.interp(self.departments[dep]["items"],
                                                               [self.config["items"][dep][0] - 0.5,
                                                                self.config["items"][dep][1],
                                                                self.config["items"][dep][2] + 0.5],
                                                               [0.0, 2 / (self.config["items"][dep][2] -
                                                                          self.config["items"][dep][0] + 1), 0.0])
            # correct for slight errors in interploation to ensure P(omega)=1
            self.departments[dep]["probabilities"] /= np.sum(self.departments[dep]["probabilities"])

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
        for dep in self.departments.keys():
            shopping_list[dep] = int(self.rng.choice(self.departments[dep]["items"],
                                                     p=self.departments[dep]["probabilities"]))
        basket = bool(self.rng.binomial(1, self.config["basket"], 10)[0])
        route = self.rng.choice(self.routes, p=self.route_probabilities)
        seed = self.rng.integers(0, sys.maxsize, 1)[0]

        return Customer(self.env, self.config["stochastics"], self.resources, self.config["flags"], shopping_list, basket, route, t, ucid, seed)

    def average_wait_time(self):
        N_customers = len(self.customers)
        return {
            "baskets" : sum([customer.wait_times['entrance'] for customer in self.customers if customer.basket]) / N_customers,
            "shopping carts": sum(
                [customer.wait_times['entrance'] for customer in self.customers if not customer.basket]) / N_customers,
            "bread": sum(
                [customer.wait_times['bread'] for customer in self.customers]) / N_customers,
            "cheese": sum(
                [customer.wait_times['cheese'] for customer in self.customers]) / N_customers,
            "checkout": sum(
                [customer.wait_times['checkout'] for customer in self.customers]) / N_customers,

        }


