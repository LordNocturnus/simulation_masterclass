import numpy.random as npr

class Customer:

    def __init__(self, env, shopping_list: dict[str, int], basket: bool, route: str, start_time: float,
                 search_bounds: (float, float), ucid: int, seed: int):
        self.env = env
        self.shopping_list = shopping_list
        self.basket = basket
        self.route = route
        self.start_time = start_time
        self.ucid = ucid # unique customer id
        self.search_bounds = search_bounds
        self.rng = npr.default_rng(seed)

        print(f"{ucid} entered at {start_time}")