from src.queuing import checkoutProcess, breadQueue, cheeseQueue
from src.department import function_dict, checkout_wrapper, generic_department_function
class Customer:

    def __init__(self, env, resources: dict, shopping_list: dict[str, int], basket: bool, path: str, start_time: float, ucid: int):
        self.env = env
        self.resources = resources
        self.shopping_list = shopping_list
        self.basket = basket
        self.path = path
        self.start_time = start_time
        self.ucid = ucid

        self.env.process(self.run())

        # print(f"{ucid} entered at {start_time}")

    def total_items(self):
        # total number of items in the shopping list
        return sum([value for key, value in self.shopping_list.items()])

    # MAIN CUSTOMER ROUTINE FUNCTION
    def run(self):
        # wait to enter the store
        yield self.env.timeout(self.start_time)
        print('{} enters the store at {}'.format(self.ucid, self.env.now))

        # choose basker or cart to pick at the entrance
        if self.basket:
            container = self.resources["baskets"]
        else:
            container = self.resources["shopping carts"]

        with container.request() as rq:
            # wait until a container is free
            yield rq
            print('{} picks a basket'.format(self.ucid) if self.basket else '{} picks a shopping cart'.format(self.ucid))

            # loop over the departments on the intended path
            # (assuming self.path is a string of lowercase characters)!
            for current_department in self.path:
                department_routine = function_dict[current_department]  # pick the right routine function
                routine = self.env.process(department_routine(self, self.env, current_department))
                yield routine  # execute routine at each department

            # checkout
            checkout = self.env.process(checkout_wrapper(self, self.env))
            yield checkout






