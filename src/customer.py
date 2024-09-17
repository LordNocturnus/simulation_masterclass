from src.TracedResource import checkout_process, bread_queue, cheese_queue
from src.department import function_dict, checkout_wrapper, generic_department_function
from scipy.stats import truncnorm
from operator import itemgetter
import numpy.random as npr
import numpy as np



class Customer:

    def __init__(self, env, stochastics:dict, departments: dict, resources: dict, flags:dict,
                 shopping_list: dict[str, int], basket: bool, route: str, start_time, ucid, seed):
        self.env = env
        self.resources = resources
        self.departments = departments
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
        # for containers its without
        self.use_times = {}
        self.store_time = 0.0

        self.action = self.env.process(self.run())

    def total_items(self):
        # total number of items in the shopping list
        return sum([value for key, value in self.shopping_list.items()])

    @property
    def wait_time_container(self):
        """ time customer is waiting for container"""
        try:
            return self.wait_times["container"]
        except KeyError:
            return 0.0

    @property
    def wait_time_checkout(self):
        """ time customer is waiting for checkout"""
        try:
            return self.wait_times["checkout"]
        except KeyError:
            return 0.0

    def wait_time_department(self, department):
        """ time customer is waiting at a specific department"""
        try:
            return self.wait_times[department]
        except KeyError:
            return 0.0

    @property
    def use_time_container(self):
        """ time customer is in possession of a container"""
        try:
            return self.use_times["container"]
        except KeyError:
            return 0.0

    @property
    def use_time_checkout(self):
        """ time customer is at a checkout (includes waiting time in checkout queue)"""
        try:
            return self.use_times["checkout"]
        except KeyError:
            return 0.0

    def use_time_department(self, department):
        """ time customer is in a department (does include waiting times in departments with queues)"""
        try:
            return self.use_times[department]
        except KeyError:
            return 0.0

    @property
    def active_time_checkout(self):
        """ time customer is using a checkout"""
        try:
            return self.use_times["checkout"] - self.wait_times["checkout"]
        except KeyError:
            return 0.0

    def active_time_department(self, department):
        """ time customer is in a department getting items (does not include waiting time)"""
        try:
            return self.use_times[department] - self.wait_times[department]
        except KeyError:
            try:
                return self.use_times[department]
            except KeyError:
                return 0.0

    # MAIN CUSTOMER ROUTINE FUNCTION
    def run(self):
        # wait to enter the store
        yield self.env.timeout(self.start_time)

        # choose basket or cart to pick at the entrance
        if self.basket:
            container = self.resources["baskets"]
        else:
            container = self.resources["shopping_carts"]

        with container.request() as container_request:
            container_start = self.env.now
            yield container_request
            self.wait_times["container"] = self.env.now - container_start
            container_hold = self.env.now

            # iterate through department path
            for department_id in self.route:
                department_start = self.env.now
                current_department = self.departments[department_id]
                if self.flags["print"]:
                    print('{:.2f}: {} enters department {}'.format(self.env.now, self.ucid,
                                                                   current_department.name))

                if current_department.queue is not None:
                    # departments with queue
                    with current_department.queue.request() as department_request:
                        yield department_request
                        self.wait_times[department_id] = self.env.now - department_start
                        yield self.env.timeout(current_department.rv.rvs(random_state=self.rng.integers(0, 2**32 - 1)))
                else:
                    # departments with no queue
                    for i in range(self.shopping_list[department_id]):
                        yield self.env.timeout(self.rng.uniform(self.stochastics["search_bounds"][0],
                                                                self.stochastics["search_bounds"][1]))
                    if self.flags["print"]:
                        print('{:.2f}: {} picks {} items at department {} in {:.2f} seconds'.format(self.env.now,
                                                                                                    self.ucid,
                                                                                                    self.shopping_list[
                                                                                                        department_id],
                                                                                                    department_id,
                                                                                                    self.env.now - department_start))
                if self.flags["print"]:
                    print('{:.2f}: {} leaves department {}'.format(self.env.now, self.ucid, department_id))
                self.use_times[department_id] = self.env.now - department_start

            # checkout
            if self.flags["print"]:
                print('{:.2f}: {} enters checkout'.format(self.env.now, self.ucid))

            # find the shortest queue
            idx, _ = min(enumerate(len(ch.put_queue) + ch.count for ch in self.resources["checkouts"]),
                         key=itemgetter(1))
            checkout = self.resources["checkouts"][idx]

            with checkout.request() as checkout_request:
                checkout_start = self.env.now
                yield checkout_request
                self.wait_times["checkout"] = self.env.now - checkout_start

                if self.flags["print"]:
                    print('{:.2f}: {} scans items at checkout'.format(self.env.now, self.ucid))

                t_scan = truncnorm.rvs(-4, 4, loc=self.stochastics["scan_vars"][0],
                                       scale=self.stochastics["scan_vars"][1],
                                       random_state=self.rng.integers(0, 2**32 - 1), size=self.total_items())
                yield self.env.timeout(np.sum(t_scan))

                if self.flags["print"]:
                    print('{:.2f}: {} pays at checkout'.format(self.env.now, self.ucid))

                yield self.env.timeout(self.rng.uniform(self.stochastics["payment_bounds"][0],
                                                        self.stochastics["payment_bounds"][1]))

            self.use_times["checkout"] = self.env.now - checkout_start


        self.use_times["container"] = self.env.now - container_hold
        self.store_time = self.env.now - self.start_time
