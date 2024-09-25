from matplotlib import pyplot as plt
import numpy as np

from src.department import Department
from src.shelf import Shelf
from src.pathing import PathGrid


class Store:

    def __init__(self, env, config):
        self.env = env
        self.config = config

        self.departments = dict()

        # following values where obtained using pixel measurements from store.PNG
        self.departments["A"] = Department("A - Fruit & Vegetables", env,
                                           shelves= [Shelf(np.asarray([403.0, 1049.0]), np.asarray([810.0, 1049.0])),
                                                     Shelf(np.asarray([403.0, 1049.0]), np.asarray([403.0, 1282.0])),
                                                     Shelf(np.asarray([403.0, 1282.0]), np.asarray([810.0, 1282.0])),
                                                     Shelf(np.asarray([810.0, 1049.0]), np.asarray([810.0, 1282.0])),
                                                     Shelf(np.asarray([892.0, 1049.0]), np.asarray([1299.0, 1049.0])),
                                                     Shelf(np.asarray([892.0, 1049.0]), np.asarray([892.0, 1282.0])),
                                                     Shelf(np.asarray([892.0, 1282.0]), np.asarray([1299.0, 1282.0])),
                                                     Shelf(np.asarray([1299.0, 1049.0]), np.asarray([1299.0, 1282.0])),
                                                     Shelf(np.asarray([1371.0, 1049.0]), np.asarray([1777.0, 1049.0])),
                                                     Shelf(np.asarray([1371.0, 1049.0]), np.asarray([1371.0, 1282.0])),
                                                     Shelf(np.asarray([1371.0, 1282.0]), np.asarray([1777.0, 1282.0])),
                                                     Shelf(np.asarray([1777.0, 1049.0]), np.asarray([1777.0, 1282.0])),
                                                     Shelf(np.asarray([409.0, 1441.0]), np.asarray([815.0, 1441.0])),
                                                     Shelf(np.asarray([897.0, 1441.0]), np.asarray([1304.0, 1441.0])),
                                                     Shelf(np.asarray([1376.0, 1441.0]), np.asarray([1701.0, 1441.0])),
                                                     ])
        self.departments["B"] = Department("B - Meat & Fish", env,
                                           shelves= [Shelf(np.asarray([409.0, 1511.0]), np.asarray([815.0, 1511.0])),
                                                     Shelf(np.asarray([897.0, 1511.0]), np.asarray([1304.0, 1511.0])),
                                                     Shelf(np.asarray([1376.0, 1511.0]), np.asarray([1701.0, 1511.0])),
                                                     Shelf(np.asarray([276.0, 1660.0]), np.asarray([1701.0, 1660.0])),
                                                     ])
        self.departments["C"] = Department("C - Bread", env, self.config["resource quantities"]["bread clerks"],
                                           self.config["Customer"]["stochastics"]["bread_vars"],
                                           shelves= [])
        self.departments["D"] = Department("D - Cheese", env, self.config["resource quantities"]["cheese clerks"],
                                           self.config["Customer"]["stochastics"]["cheese_vars"],
                                           shelves= [Shelf(np.asarray([0.0, 72.0]), np.asarray([275.0, 72.0])),
                                                     Shelf(np.asarray([0.0, 148.0]), np.asarray([275.0, 148.0])),
                                                     Shelf(np.asarray([0.0, 220.0]), np.asarray([275.0, 220.0])),
                                                     Shelf(np.asarray([0.0, 306.0]), np.asarray([275.0, 306.0])),])
        self.departments["E"] = Department("E - Canned & packed food", env,
                                           shelves= [Shelf(np.asarray([275.0, 72.0]), np.asarray([1915.0, 72.0])),
                                                     Shelf(np.asarray([357.0, 153.0]), np.asarray([357.0, 865.0])),
                                                     Shelf(np.asarray([428.0, 153.0]), np.asarray([428.0, 865.0])),
                                                     Shelf(np.asarray([510.0, 153.0]), np.asarray([510.0, 865.0])),
                                                     Shelf(np.asarray([581.0, 153.0]), np.asarray([581.0, 865.0])),
                                                     Shelf(np.asarray([663.0, 153.0]), np.asarray([663.0, 865.0])),
                                                     Shelf(np.asarray([733.0, 153.0]), np.asarray([733.0, 865.0])),
                                                     Shelf(np.asarray([816.0, 153.0]), np.asarray([816.0, 865.0])),
                                                     Shelf(np.asarray([886.0, 153.0]), np.asarray([886.0, 865.0])),
                                                     Shelf(np.asarray([959.0, 153.0]), np.asarray([959.0, 865.0])),
                                                     Shelf(np.asarray([1029.0, 153.0]), np.asarray([1029.0, 865.0])),
                                                     Shelf(np.asarray([1111.0, 153.0]), np.asarray([1111.0, 865.0])),
                                                     Shelf(np.asarray([1181.0, 153.0]), np.asarray([1181.0, 865.0])),
                                                     Shelf(np.asarray([1264.0, 153.0]), np.asarray([1264.0, 865.0])),
                                                     Shelf(np.asarray([1334.0, 153.0]), np.asarray([1334.0, 865.0])),
                                                     Shelf(np.asarray([1417.0, 153.0]), np.asarray([1417.0, 865.0])),
                                                     Shelf(np.asarray([1487.0, 153.0]), np.asarray([1487.0, 865.0])),
                                                     Shelf(np.asarray([1559.0, 153.0]), np.asarray([1559.0, 865.0])),
                                                     Shelf(np.asarray([1630.0, 153.0]), np.asarray([1630.0, 865.0])),
                                                     Shelf(np.asarray([1712.0, 153.0]), np.asarray([1712.0, 865.0])),
                                                     Shelf(np.asarray([1782.0, 153.0]), np.asarray([1782.0, 865.0])),])
        self.departments["F"] = Department("F - Frozen food", env,
                                           shelves= [Shelf(np.asarray([2071.0, 78.0]), np.asarray([1904.0, 366.0])),
                                                     Shelf(np.asarray([2133.0, 114.0]), np.asarray([1965.0, 402.0])),
                                                     Shelf(np.asarray([2250.0, 78.0]), np.asarray([2083.0, 366.0])),
                                                     Shelf(np.asarray([2312.0, 114.0]), np.asarray([2144.0, 402.0])),
                                                     Shelf(np.asarray([2402.0, 78.0]), np.asarray([2235.0, 366.0])),
                                                     Shelf(np.asarray([2464.0, 114.0]), np.asarray([2297.0, 402.0])),
                                                     Shelf(np.asarray([2567.0, 87.0]), np.asarray([2401.0, 376.0])),
                                                     Shelf(np.asarray([2629.0, 123.0]), np.asarray([2462.0, 412.0])),
                                                     Shelf(np.asarray([2720.0, 87.0]), np.asarray([2553.0, 376.0])),
                                                     Shelf(np.asarray([2780.0, 128.0]), np.asarray([2615.0, 412.0])),
                                                     ])
        self.departments["G"] = Department("G - Drinks", env,
                                           shelves= [Shelf(np.asarray([1986.0, 479.0]), np.asarray([1986.0, 1048.0])),
                                                     Shelf(np.asarray([2068.0, 479.0]), np.asarray([2068.0, 1048.0])),
                                                     Shelf(np.asarray([2139.0, 479.0]), np.asarray([2139.0, 1048.0])),
                                                     Shelf(np.asarray([2231.0, 479.0]), np.asarray([2231.0, 1048.0])),
                                                     Shelf(np.asarray([2302.0, 479.0]), np.asarray([2302.0, 1048.0])),
                                                     Shelf(np.asarray([2384.0, 479.0]), np.asarray([2384.0, 1048.0])),
                                                     Shelf(np.asarray([2455.0, 479.0]), np.asarray([2455.0, 1048.0])),
                                                     Shelf(np.asarray([2557.0, 479.0]), np.asarray([2557.0, 1048.0])),
                                                     Shelf(np.asarray([2628.0, 479.0]), np.asarray([2628.0, 1048.0])),
                                                     Shelf(np.asarray([2710.0, 479.0]), np.asarray([2710.0, 1048.0])),])

        self.path_grid = PathGrid()
        self.path_grid.add_node(np.asarray([1809.0, 1730.0])) # 0
        self.path_grid.add_node(np.asarray([1809.0, 1603.0])) # 1
        self.path_grid.add_edge(0, 1, False)
        self.path_grid.add_node(np.asarray([1846.5, 1361.5])) # 2
        self.path_grid.add_edge(1, 2, False)
        self.path_grid.add_node(np.asarray([1340, 1361.5])) # 3
        self.path_grid.add_edge(2, 3)
        self.path_grid.add_node(np.asarray([1335, 1361.5])) # 4
        self.path_grid.add_edge(3, 4)
        self.path_grid.add_node(np.asarray([856, 1361.5])) # 5
        self.path_grid.add_edge(4, 5)
        self.path_grid.add_node(np.asarray([851, 1361.5])) # 6
        self.path_grid.add_edge(5, 6)
        self.path_grid.add_node(np.asarray([342, 1361.5])) # 7
        self.path_grid.add_edge(6, 7)
        self.path_grid.add_node(np.asarray([339.5, 1361.5])) # 8
        self.path_grid.add_edge(7, 8)
        self.path_grid.add_node(np.asarray([1340, 1585])) # 9
        self.path_grid.add_edge(3, 9)
        self.path_grid.add_node(np.asarray([1701, 1585])) # 10
        self.path_grid.add_edge(9, 10)
        self.path_grid.add_node(np.asarray([856, 1585])) # 11
        self.path_grid.add_edge(9, 11)
        self.path_grid.add_edge(5, 11)
        self.path_grid.add_node(np.asarray([342, 1585])) # 12
        self.path_grid.add_edge(11, 12)
        self.path_grid.add_edge(7, 12)
        self.path_grid.add_node(np.asarray([1846.5, 1084])) # 13
        self.path_grid.add_edge(2, 13)
        self.path_grid.add_node(np.asarray([1846.5, 957])) # 14
        self.path_grid.add_edge(13, 14)
        self.path_grid.add_node(np.asarray([1849, 957])) # 15
        self.path_grid.add_edge(14, 15)
        self.path_grid.add_node(np.asarray([1671, 957])) # 16
        self.path_grid.add_edge(14, 16)
        self.path_grid.add_node(np.asarray([1523, 957])) # 17
        self.path_grid.add_edge(16, 17)
        self.path_grid.add_node(np.asarray([1375.5, 957])) # 18
        self.path_grid.add_edge(17, 18)
        self.path_grid.add_node(np.asarray([1335, 957])) # 19
        self.path_grid.add_edge(18, 19)
        self.path_grid.add_edge(4, 19)
        self.path_grid.add_node(np.asarray([1223, 957])) # 20
        self.path_grid.add_edge(19, 20)
        self.path_grid.add_node(np.asarray([1070, 957])) # 21
        self.path_grid.add_edge(20, 21)
        self.path_grid.add_node(np.asarray([922.5, 957])) # 22
        self.path_grid.add_edge(21, 22)
        self.path_grid.add_node(np.asarray([851, 957])) # 23
        self.path_grid.add_edge(22, 23)
        self.path_grid.add_edge(6, 23)
        self.path_grid.add_node(np.asarray([775, 957])) # 24
        self.path_grid.add_edge(23, 24)
        self.path_grid.add_node(np.asarray([622, 957])) # 25
        self.path_grid.add_edge(24, 25)
        self.path_grid.add_node(np.asarray([469, 957])) # 26
        self.path_grid.add_edge(25, 26)
        self.path_grid.add_node(np.asarray([339.5, 957])) # 27
        self.path_grid.add_edge(26, 27)
        self.path_grid.add_edge(7, 27)
        self.path_grid.add_node(np.asarray([316.5, 957])) # 28
        self.path_grid.add_edge(27, 28)

        self.scale(np.asarray([2780.0, 1730.0]), np.asarray([40.0, 30.0]))

    def scale(self, old, new):
        # scale each department using old and new extends of the store
        for key in self.departments:
            self.departments[key].scale(old, new)

        self.path_grid.scale(old, new)

    def plot(self):
        for department in self.departments.values():
            for shelf in department.shelves:
                plt.plot([shelf.start[0], shelf.end[0]], [-shelf.start[1], -shelf.end[1]], color="r")

        for edge in self.path_grid.edges:
            plt.plot([edge.start.pos[0], edge.end.pos[0]], [-edge.start.pos[1], -edge.end.pos[1]], color="b",
                     marker="x")

        plt.show()
