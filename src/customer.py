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

        # request storage
        self.requests = {}

        # time stamps
        self.arrival_times = {

        }
        self.serve_times = {

        }
        self.release_times = {

        }

        # time intervals
        self.wait_times = {
        }
        self.use_times = {
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

    def departmentRouting(self):
        # loop over the departments on the intended path
        for current_department in self.route:
            department_routine = function_dict[current_department]  # pick the right routine function
            routine = self.env.process(department_routine(self, self.env, current_department))
            yield routine  # execute routine at each department

        # checkout
        checkout = self.env.process(checkout_wrapper(self, self.env))
        yield checkout

    def resourceRequestBlock(self, resource, subroutine, *args, **kwargs):
        """
        wrapper around the .request() method, including the logging of relevant events
        function essentially replaces the "with self.request() as req:" block
        WARNING: implement with caution, as the request block has to be:
         1) wrapped in the env.process() function to execute process
         see implementation in the checkoutQueue, breadQueue, and cheeseQueue for reference
        :param resource: a TracedResource to queue up, use, and release
        :param subroutine: a function including a yield statement or another subroutine
        :param *args,**kwargs: params to pass to the subroutine function (if any!)
        """
        resource.ucids.add(self.ucid)  # add ucid to set of users of this resource

        self.requests[resource.name] = resource.request()

        if self.flags["print"]:
            print('{:.2f}: {} enters a {} queue'.format(resource.env.now, self.ucid, resource.name))

        self.arrival_times[resource.name] = resource.env.now
        resource.queueLog.append(
            {
                "ucid": self.ucid,
                "time": self.arrival_times[resource.name],
                "value": 1
            }
        )
        resource.demandLog.append(
            {
                "ucid": self.ucid,
                "time": self.arrival_times[resource.name],
                "value": 1
            }
        )
        yield self.requests[resource.name]  # wait to be served

        self.serve_times[resource.name] = resource.env.now

        # queueLog queue exit
        resource.queueLog.append(
            {
                "ucid": self.ucid,
                "time": self.serve_times[resource.name],
                "value": -1
            }
        )
        self.wait_times[resource.name] = self.serve_times[resource.name] - self.arrival_times[resource.name]

        if self.flags["print"]:
            print('{:.2f}: {} is served at {}'.format(resource.env.now, self.ucid, resource.name))

        # log use
        resource.capacityLog.append(
            {
                "ucid": self.ucid,
                "time": self.serve_times[resource.name],
                "value": 1
            }
        )

        # yield subprocess
        yield self.env.process(subroutine(*args, **kwargs))

        if self.flags["print"]:
            print('{:.2f}: {} finishes action at {}'.format(resource.env.now, self.ucid, resource.name))

        self.release_times[resource.name] = resource.env.now
        resource.release(self.requests[resource.name])

        # log end of use
        resource.capacityLog.append(
            {
                "ucid": self.ucid,
                "time": self.release_times[resource.name],
                "value": -1
            }
        )
        resource.demandLog.append(
            {
                "ucid": self.ucid,
                "time": self.release_times[resource.name],
                "value": -1
            }
        )

        self.use_times[resource.name] = self.release_times[resource.name] - self.serve_times[resource.name]

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

        # execute routine while using a resource (basker or shopping cart)
        # subprocess = self.env.process(self.departmentRouting())
        processBlock = self.env.process(self.resourceRequestBlock(container, self.departmentRouting))
        # yield processBlock

        if self.flags["print"]:
            print('{:.2f}: {} leaves the store'.format(self.env.now, self.ucid))








