from scipy.stats import truncnorm
from operator import itemgetter
import numpy.random as npr
import numpy as np

from src.store import Store


class Customer:

    def __init__(self, env, stochastics:dict, store: Store, resources: dict, flags:dict,
                 shopping_list: dict[str, int], basket: bool, route: str, start_time: float, walking_speed: float,
                 ucid: int, seed: int):
        self.env = env
        self.resources = resources
        self.store = store
        self.shopping_list = shopping_list
        self.basket = basket
        self.route = route
        self.start_time = start_time
        self.ucid = ucid # unique customer id
        self.rng = npr.default_rng(seed)
        self.stochastics = stochastics
        self.flags = flags
        self.walking_speed = walking_speed # walking speed in m/s
        # initialize wait times and use times of resources
        self.wait_times = {}
        self.use_times = {}
        self.store_time = 0.0

        # Everything related to allowing customers to walk
        self.walking = False
        self.walking_start_time = 0.0
        self.walking_direction = np.zeros(2, dtype=np.float64)
        self._pos = np.zeros(2, dtype=np.float64)
        self.on_node = None # None if not on a node otherwise equal to node id
        self.current_department_id = None
        self.closest_edge = None # closets edge to the current position
        self.reserved_edge = None

        self.draw = False
        self.color = (0, 0, 255)

        self.action = self.env.process(self.run())

    @property
    def pos(self):
        if not self.walking:
            return self._pos
        return self._pos + self.walking_direction * (self.env.now - self.walking_start_time)

    @property
    def total_items(self):
        # total number of items in the shopping list
        return sum([value for key, value in self.shopping_list.items()])

    def total_time(self, key):
        return self.wait_times[key] + self.use_times[key]

    @property
    def exit_time(self):
        # the time the customer exits the store
        return self.store_time + self.start_time

    def walk(self, destination):
        # customer sub process for walking from one location to the next
        self.walking_start_time = self.env.now
        walking_time = np.linalg.norm(destination - self.pos) / self.walking_speed
        self.walking_direction = (destination - self.pos) / walking_time
        self.walking = True
        yield self.env.timeout(walking_time)
        self.walking = False
        # only update location after arrival not during walking
        self._pos = destination

    def path_to(self, destination, dep=None):
        """
        path to the given destination.
        destination can be a position or index of a node in the path grid
        """
        if self.on_node is None:
            path = self.store.path_grid.dijkstra(self.pos, destination, self.current_department_id, dep)
        else:
            path = self.store.path_grid.dijkstra(self.on_node, destination, self.current_department_id, dep)

        if not isinstance(destination, int):
            path = path[:-1]

        for node_id in path:
            node = self.store.path_grid.nodes[node_id]
            if not self.basket and self.on_node is not None:
                edge = node.incoming_edges[self.on_node]
                if edge.blockage is not None:
                    req = edge.blockage.request()
                    self.reserved_edge = (edge, req)
                    self.color = (255, 0, 0)
                    yield req
                    self.color = (0, 0, 255)
            yield self.env.process(self.walk(node.pos))
            if self.reserved_edge is not None:
                self.reserved_edge[0].blockage.release(self.reserved_edge[1])
                self.reserved_edge = None
            self.on_node = node_id

        if not isinstance(destination, int):
            if not self.basket:
                edge = self.store.path_grid.get_closest_edge(destination, dep)
                if edge.blockage is not None:
                    req = edge.blockage.request()
                    self.reserved_edge = (edge, req)
                    self.color = (255, 0, 0)
                    yield req
                    self.color = (0, 0, 255)
            yield self.env.process(self.walk(destination))
            self.on_node = None
        self.current_department_id = dep



    # MAIN CUSTOMER ROUTINE FUNCTION
    def run(self):
        # wait to enter the store
        yield self.env.timeout(self.start_time)

        # customer has entered the store so we start drawing it
        self.draw = True

        # customer enters store at the entrance node
        self._pos = self.store.path_grid.nodes[0].pos
        self.on_node = 0

        # choose basket or cart to pick at the entrance
        if self.basket:
            container = self.resources["baskets"]
        else:
            container = self.resources["shopping_carts"]

        with container.request() as container_request:
            container_wait = self.env.now
            self.color = (255, 0, 0)
            yield container_request & self.env.process(self.path_to(1))
            self.color = (0, 0, 255)
            self.on_node = 1
            self.wait_times["container"] = self.env.now - container_wait
            container_use = self.env.now

            # iterate through department path
            for department_id in self.route:
                department_wait = self.env.now
                current_department = self.store.departments[department_id]

                # log department entry
                current_department.log_event.append(1)
                current_department.log_time.append(self.env.now)
                if self.flags["print"]:
                    print('{:.2f}: {} enters department {}'.format(self.env.now, self.ucid,
                                                                   current_department.name))

                if current_department.queue is not None:
                    # departments with queue
                    with current_department.queue.request() as department_request:
                        self.color = (255, 0, 0)
                        yield department_request
                        self.color = (0, 255, 0)
                        self.wait_times[department_id] = self.env.now - department_wait
                        department_use = self.env.now
                        yield self.env.timeout(current_department.rv.rvs(random_state=self.rng.integers(0, 2**32 - 1)))
                else:
                    # departments with no queue
                    self.wait_times[department_id] = self.env.now - department_wait
                    department_use = self.env.now
                    for i in range(self.shopping_list[department_id]):
                        item_pos = current_department.get_item_location(self.rng)

                        if self.flags["print"]:
                            print('{:.2f}: {} walking from ({:.2f},{:.2f}) to ({:.2f},{:.2f})'.format(
                                self.env.now, self.ucid, self.pos[0], self.pos[1], item_pos[0], item_pos[1]))
                        walking = self.env.process(self.path_to(item_pos, department_id))
                        self.color = (0, 0, 255)
                        yield walking
                        self.color = (0, 255, 0)
                        if self.flags["print"]:
                            print('{:.2f}: {} picks up item at ({:.2f},{:.2f})'.format(self.env.now, self.ucid,
                                                                                       item_pos[0], item_pos[1]))
                        yield self.env.timeout(self.rng.uniform(self.stochastics["search_bounds"][0],
                                                                self.stochastics["search_bounds"][1]))
                    if self.flags["print"]:
                        print('{:.2f}: {} picked {} items at department {} in {:.2f} seconds'.format(self.env.now,
                                                                                                     self.ucid,
                                                                                                     self.shopping_list[
                                                                                                         department_id],
                                                                                                     department_id,
                                                                                                     self.env.now - department_wait))

                # log department exit
                current_department.log_event.append(-1)
                current_department.log_time.append(self.env.now)
                if self.flags["print"]:
                    print('{:.2f}: {} leaves department {}'.format(self.env.now, self.ucid, department_id))
                self.use_times[department_id] = self.env.now - department_use

            # checkout
            if self.flags["print"]:
                print('{:.2f}: {} enters checkout'.format(self.env.now, self.ucid))

            # find the shortest queue
            idx, _ = min(enumerate(len(ch.put_queue) + ch.count for ch in self.resources["checkout"]),
                         key=itemgetter(1))
            checkout = self.resources["checkout"][idx]

            with checkout.request() as checkout_request:
                checkout_wait = self.env.now
                self.color = (255, 0, 0)
                yield checkout_request
                self.color = (0, 255, 0)
                self.wait_times["checkout"] = self.env.now - checkout_wait
                checkout_use = self.env.now

                if self.flags["print"]:
                    print('{:.2f}: {} scans items at checkout'.format(self.env.now, self.ucid))

                t_scan = truncnorm.rvs(-4, 4, loc=self.stochastics["scan_vars"][0],
                                       scale=self.stochastics["scan_vars"][1],
                                       random_state=self.rng.integers(0, 2**32 - 1), size=self.total_items)
                yield self.env.timeout(np.sum(t_scan))

                # cashier has to ask for price
                if self.rng.uniform(0.0, 1.0) < 0.05:
                    yield self.env.timeout(self.rng.exponential(12))

                if self.flags["print"]:
                    print('{:.2f}: {} pays at checkout'.format(self.env.now, self.ucid))

                yield self.env.timeout(self.rng.uniform(self.stochastics["payment_bounds"][0],
                                                        self.stochastics["payment_bounds"][1]))

                # cashier has to check payment
                if self.rng.uniform(0.0, 1.0) < 0.02:
                    yield self.env.timeout(self.rng.uniform(30, 45))

            self.use_times["checkout"] = self.env.now - checkout_use

        self.use_times["container"] = self.env.now - container_use
        self.store_time = self.env.now - self.start_time

        # customer has left the store so we stop drawing it
        self.draw = False
