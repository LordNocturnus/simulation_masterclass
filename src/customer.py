from src.queuing import checkoutProcess, breadQueue, cheeseQueue
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
        # initialize wait times as 0.0
        self.wait_times = {
            "entrance" : 0.0,
            "bread" : 0.0,
            "cheese" : 0.0,
            "checkout" : 0.0
        }

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

    # MAIN CUSTOMER ROUTINE FUNCTION
    def run(self):
        # wait to enter the store

        yield self.env.timeout(self.start_time)




        if self.flags["print"]:
            print('{:.2f}: {} enters the store'.format(self.env.now, self.ucid))
        # choose basker or cart to pick at the entrance
        if self.basket:
            container = self.resources["baskets"]
        else:
            container = self.resources["shopping carts"]

        with container.request() as rq:
            # wait until a container is free
            if self.flags["print"]:
                print('{:.2f}: {} enters a queue for a basket'.format(self.env.now, self.ucid) if self.basket
                  else '{:.2f}: {} enters a queue for a shopping cart'.format(self.env.now, self.ucid))

            t0 = self.env.now
            # log queue entry
            container.queueLog.append(
                {
                    "ucid": self.ucid,
                    "time": t0,
                    "value": 1
                }
            )
            yield rq
            t1 = self.env.now
            # log queue exit
            container.queueLog.append(
                {
                    "ucid": self.ucid,
                    "time": t1,
                    "value": -1
                }
            )
            # log container use
            container.capacityLog.append(
                {
                    "ucid": self.ucid,
                    "time": t1,
                    "value": 1
                }
            )

            # store wait time
            self.wait_times["entrance"] = t1 - t0

            if self.flags["print"]:
                print('{:.2f}: {} picks a basket'.format(self.env.now,self.ucid) if self.basket
                      else '{:.2f}: {} picks a shopping cart'.format(self.env.now, self.ucid))

            # loop over the departments on the intended path
            # (assuming self.path is a string of lowercase characters)!
            for current_department in self.route:
                department_routine = function_dict[current_department]  # pick the right routine function
                routine = self.env.process(department_routine(self, self.env, current_department))
                yield routine  # execute routine at each department

            # checkout
            checkout = self.env.process(checkout_wrapper(self, self.env))
            yield checkout

        # log container being freed
        container.capacityLog.append(
            {
                "ucid": self.ucid,
                "time": self.env.now,
                "value":-1
            }
        )







