from numpy import random as npr
import numpy as np
import json


from src.customer import Customer


class CustomerFactory:

    def __init__(self, env, customer_config, seed=0):
        self.env = env
        self.customers = []
        self.rng = npr.default_rng(seed)
        with open(customer_config) as config:
            self.config = json.load(config)["Customer"]
        ucid = 0
        for k, v in enumerate(self.config["arrivals"][:-1]):
            count = int(np.round(self.rng.normal(v[1], v[2] / 2)))
            for _ in range(count):
                t = self.rng.uniform(v[0], self.config["arrivals"][k+1][0], 1)
                shopping_list = {}
                for dep in self.config["items"].keys():
                    shopping_list[dep] = int(self.rng.integers(self.config["items"][dep][0],
                                                               self.config["items"][dep][2]))
                basket = self.rng.uniform(0, 1) <= self.config["basket"]
                print(shopping_list)
                print(t)
                break
            break
            #print(count)
            #print(v)

