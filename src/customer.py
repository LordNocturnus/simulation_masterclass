from src.TracedResource import checkout_process, bread_queue, cheese_queue
from src.department import function_dict, checkout_wrapper, generic_department_function
import numpy.random as npr


class Customer:

    def __init__(self, env, stochastics:dict, resources: dict, flags:dict,
                 shopping_list: dict[str, int], basket: bool, route: str, start_time, ucid, seed):
        self.env = env
        self.resources = resources
        self.shopping_list = shopping_list
        self.basket = basket
        self.route = route
        self.start_time = start_time
        self.ucid = ucid # unique customer id
        self.rng = npr.default_rng(seed)
        self.stochastics = stochastics
        self.flags = flags
        # initialize wait times and use times of resources
        self.wait_times = {}
        self.use_times = {}

        self.action = self.env.process(self.run())

    def total_items(self):
        # total number of items in the shopping list
        return sum([value for key, value in self.shopping_list.items()])

    def time_string(self, time=None):
        if time:
            s = time
        else:
            s = self.env.now
        h = int(s//3600)
        m = int((s-h*3600)//60)
        s = int((s - h*3600 - m*60))
        return "{:02d}:{:02d}:{:02d}".format(h+8, m,s)

    def DepartmentSubprocess(self):
        # loop over the departments on the intended path
        for current_department in self.route:
            department_routine = function_dict[current_department]  # pick the right routine function
            routine = self.env.process(department_routine(self, self.env, current_department))
            yield routine  # execute routine at each department

        # checkout
        checkout = self.env.process(checkout_wrapper(self, self.env))
        yield checkout

    # MAIN CUSTOMER ROUTINE FUNCTION
    def run(self):
        # wait to enter the store
        yield self.env.timeout(self.start_time)

        # choose basker or cart to pick at the entrance
        if self.basket:
            container = self.resources["baskets"]
        else:
            container = self.resources["shopping carts"]

        # run subprocess while requesting a container
        subprocess = self.env.process(self.DepartmentSubprocess())
        processBlock = self.env.process(container.request_block(self, subprocess))
        yield processBlock
