import numpy.random as npr

class Customer:

    def __init__(self, env, shopping_list, basket, route, start_time, search_bounds, ucid, seed):
        self.env = env
        self.shopping_list = shopping_list
        self.basket = basket
        self.route = route
        self.start_time = start_time
        self.ucid = ucid # unique customer id
        self.search_bounds = search_bounds
        self.rng = npr.default_rng(seed)

        self.action = self.env.process(self.run())

    def run(self):
        yield self.env.timeout(self.start_time)
        print(f"{self.ucid} entered at {self.start_time}")
