

class Customer:

    def __init__(self, env, shopping_list: dict[str, int], basket: bool, path: str, start_time: float, ucid: int):
        self.env = env
        self.shopping_list = shopping_list
        self.basket = basket
        self.path = path
        self.start_time = start_time
        self.ucid = ucid

        print(f"{ucid} entered at {start_time}")