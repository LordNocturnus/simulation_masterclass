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
        self.path_grid.add_edge(1, 2, False, departments=["A"])
        self.path_grid.add_node(np.asarray([1340, 1361.5])) # 3
        self.path_grid.add_edge(2, 3, departments=["A"])
        self.path_grid.add_node(np.asarray([1335, 1361.5])) # 4
        self.path_grid.add_edge(3, 4, departments=["A"])
        self.path_grid.add_node(np.asarray([856, 1361.5])) # 5
        self.path_grid.add_edge(4, 5, departments=["A"])
        self.path_grid.add_node(np.asarray([851, 1361.5])) # 6
        self.path_grid.add_edge(5, 6, departments=["A"])
        self.path_grid.add_node(np.asarray([342, 1361.5])) # 7
        self.path_grid.add_edge(6, 7, departments=["A"])
        self.path_grid.add_node(np.asarray([339.5, 1361.5])) # 8
        self.path_grid.add_edge(7, 8, departments=["A"])
        self.path_grid.add_node(np.asarray([1340, 1585])) # 9
        self.path_grid.add_edge(3, 9, departments=["A", "B"])
        self.path_grid.add_node(np.asarray([1701, 1585])) # 10
        self.path_grid.add_edge(9, 10, departments=["B"])
        self.path_grid.add_node(np.asarray([856, 1585])) # 11
        self.path_grid.add_edge(9, 11, departments=["B"])
        self.path_grid.add_edge(5, 11, departments=["A", "B"])
        self.path_grid.add_node(np.asarray([342, 1585])) # 12
        self.path_grid.add_edge(11, 12, departments=["B"])
        self.path_grid.add_edge(7, 12, departments=["A", "B"])
        self.path_grid.add_node(np.asarray([1846.5, 1084])) # 13
        self.path_grid.add_edge(2, 13, departments=["A"])
        self.path_grid.add_node(np.asarray([1846.5, 957])) # 14
        self.path_grid.add_edge(13, 14, departments=["A"])
        self.path_grid.add_node(np.asarray([1849, 957])) # 15
        self.path_grid.add_edge(14, 15, departments=["A"])
        self.path_grid.add_node(np.asarray([1671, 957])) # 16
        self.path_grid.add_edge(14, 16, departments=["A"])
        self.path_grid.add_node(np.asarray([1523, 957])) # 17
        self.path_grid.add_edge(16, 17, departments=["A"])
        self.path_grid.add_node(np.asarray([1375.5, 957])) # 18
        self.path_grid.add_edge(17, 18, departments=["A"])
        self.path_grid.add_node(np.asarray([1335, 957])) # 19
        self.path_grid.add_edge(18, 19, departments=["A"])
        self.path_grid.add_edge(4, 19, departments=["A"])
        self.path_grid.add_node(np.asarray([1223, 957])) # 20
        self.path_grid.add_edge(19, 20, departments=["A"])
        self.path_grid.add_node(np.asarray([1070, 957])) # 21
        self.path_grid.add_edge(20, 21, departments=["A"])
        self.path_grid.add_node(np.asarray([922.5, 957])) # 22
        self.path_grid.add_edge(21, 22, departments=["A"])
        self.path_grid.add_node(np.asarray([851, 957])) # 23
        self.path_grid.add_edge(22, 23, departments=["A"])
        self.path_grid.add_edge(6, 23, departments=["A"])
        self.path_grid.add_node(np.asarray([775, 957])) # 24
        self.path_grid.add_edge(23, 24, departments=["A"])
        self.path_grid.add_node(np.asarray([622, 957])) # 25
        self.path_grid.add_edge(24, 25, departments=["A"])
        self.path_grid.add_node(np.asarray([469, 957])) # 26
        self.path_grid.add_edge(25, 26, departments=["A"])
        self.path_grid.add_node(np.asarray([339.5, 957])) # 27
        self.path_grid.add_edge(26, 27, departments=["A"])
        self.path_grid.add_edge(8, 27, departments=["A"])
        self.path_grid.add_node(np.asarray([316.5, 957])) # 28
        self.path_grid.add_edge(27, 28, departments=["A"])
        self.path_grid.add_node(np.asarray([316.5, 262.5])) # 29
        self.path_grid.add_edge(28, 29, departments=["A", "E"])
        self.path_grid.add_node(np.asarray([0, 262.5])) # 30
        self.path_grid.add_edge(29, 30, departments=["E"])
        self.path_grid.add_node(np.asarray([316.5, 112.5])) # 31
        self.path_grid.add_edge(29, 31, departments=["E"])
        self.path_grid.add_node(np.asarray([316.5, 110])) # 32
        self.path_grid.add_edge(31, 32, departments=["E"])
        self.path_grid.add_node(np.asarray([0.0, 110])) # 33
        self.path_grid.add_edge(32, 33, departments=["E"])
        self.path_grid.add_node(np.asarray([469, 112.5])) # 34
        self.path_grid.add_edge(31, 34, departments=["E"])
        self.path_grid.add_edge(26, 34, departments=["A", "E"])
        self.path_grid.add_node(np.asarray([622, 112.5])) # 35
        self.path_grid.add_edge(34, 35, departments=["E"])
        self.path_grid.add_edge(25, 35, departments=["A", "E"])
        self.path_grid.add_node(np.asarray([775, 112.5])) # 36
        self.path_grid.add_edge(35, 36, departments=["E"])
        self.path_grid.add_edge(24, 36, departments=["A", "E"])
        self.path_grid.add_node(np.asarray([922.5, 112.5])) # 37
        self.path_grid.add_edge(36, 37, departments=["E"])
        self.path_grid.add_edge(22, 37, departments=["A", "E"])
        self.path_grid.add_node(np.asarray([1070, 112.5])) # 38
        self.path_grid.add_edge(37, 38, departments=["E"])
        self.path_grid.add_edge(21, 38, departments=["A", "E"])
        self.path_grid.add_node(np.asarray([1223, 112.5])) # 39
        self.path_grid.add_edge(38, 39, departments=["E"])
        self.path_grid.add_edge(20, 39, departments=["A", "E"])
        self.path_grid.add_node(np.asarray([1375.5, 112.5])) # 40
        self.path_grid.add_edge(39, 40, departments=["E"])
        self.path_grid.add_edge(18, 40, departments=["A", "E"])
        self.path_grid.add_node(np.asarray([1523, 112.5])) # 41
        self.path_grid.add_edge(40, 41, departments=["E"])
        self.path_grid.add_edge(17, 41, departments=["A", "E"])
        self.path_grid.add_node(np.asarray([1671, 112.5])) # 42
        self.path_grid.add_edge(41, 42, departments=["E"])
        self.path_grid.add_edge(16, 42, departments=["A", "E"])
        self.path_grid.add_node(np.asarray([1849, 112.5])) # 43
        self.path_grid.add_edge(42, 43, departments=["E"])
        self.path_grid.add_node(np.asarray([1849, 440.5])) # 44
        self.path_grid.add_edge(15, 44, departments=["A", "E"])
        self.path_grid.add_node(np.asarray([1849, 366])) # 45
        self.path_grid.add_edge(43, 45, departments=["E"])
        self.path_grid.add_edge(44, 45, departments=["E"])
        self.path_grid.add_node(np.asarray([1989.5, 112.5])) # 46
        self.path_grid.add_edge(43, 46, departments=["E", "F"])
        self.path_grid.add_edge(45, 46, departments=["E", "F"])
        self.path_grid.add_node(np.asarray([2031.5, 39])) # 47
        self.path_grid.add_edge(46, 47, departments=["F"])
        self.path_grid.add_node(np.asarray([2224, 39])) # 48
        self.path_grid.add_edge(47, 48, departments=["F"])
        self.path_grid.add_node(np.asarray([2389.5, 39])) # 49
        self.path_grid.add_edge(48, 49, departments=["F"])
        self.path_grid.add_node(np.asarray([2551.5, 39])) # 50
        self.path_grid.add_edge(49, 50, departments=["F"])
        self.path_grid.add_node(np.asarray([2713.5, 39])) # 51
        self.path_grid.add_edge(50, 51, departments=["F"])
        self.path_grid.add_node(np.asarray([1992, 440.5])) # 52
        self.path_grid.add_edge(44, 52, departments=["E", "F"])
        self.path_grid.add_edge(48, 52, departments=["F"])
        self.path_grid.add_node(np.asarray([2027, 440.5])) # 53
        self.path_grid.add_edge(52, 53, departments=["F"])
        self.path_grid.add_node(np.asarray([2158, 440.5])) # 54
        self.path_grid.add_edge(49, 54, departments=["F"])
        self.path_grid.add_edge(53, 54, departments=["F"])
        self.path_grid.add_node(np.asarray([2185, 440.5])) # 55
        self.path_grid.add_edge(54, 55, departments=["F"])
        self.path_grid.add_node(np.asarray([2319.5, 440.5])) # 56
        self.path_grid.add_edge(50, 56, departments=["F"])
        self.path_grid.add_edge(55, 56, departments=["F"])
        self.path_grid.add_node(np.asarray([2343, 440.5])) # 57
        self.path_grid.add_edge(56, 57, departments=["F"])
        self.path_grid.add_node(np.asarray([2481, 440.5])) # 58
        self.path_grid.add_edge(51, 58, departments=["F"])
        self.path_grid.add_edge(57, 58, departments=["F"])
        self.path_grid.add_node(np.asarray([2506, 440.5])) # 59
        self.path_grid.add_edge(58, 59, departments=["F"])
        self.path_grid.add_node(np.asarray([2668.5, 440.5])) # 60
        self.path_grid.add_edge(59, 60, departments=["F"])
        self.path_grid.add_node(np.asarray([2780, 246])) # 61
        self.path_grid.add_edge(60, 61, departments=["F"])
        self.path_grid.add_node(np.asarray([2027, 1084])) # 62
        self.path_grid.add_edge(13, 62, departments=["A", "G"])
        self.path_grid.add_edge(53, 62, departments=["F", "G"])
        self.path_grid.add_node(np.asarray([2032, 1084])) # 63
        self.path_grid.add_edge(62, 63, departments=["G"])
        self.path_grid.add_node(np.asarray([2185, 1084])) # 64
        self.path_grid.add_edge(55, 64, departments=["F", "G"])
        self.path_grid.add_edge(63, 64, departments=["G"])
        self.path_grid.add_node(np.asarray([2190, 1084])) # 65
        self.path_grid.add_edge(64, 65, departments=["G"])
        self.path_grid.add_node(np.asarray([2343, 1084])) # 66
        self.path_grid.add_edge(57, 66, departments=["F", "G"])
        self.path_grid.add_edge(65, 66, departments=["G"])
        self.path_grid.add_node(np.asarray([2506, 1084])) # 67
        self.path_grid.add_edge(59, 67, departments=["F", "G"])
        self.path_grid.add_edge(66, 67, departments=["G"])
        self.path_grid.add_node(np.asarray([2516, 1084])) # 68
        self.path_grid.add_edge(67, 68, departments=["G"])
        self.path_grid.add_node(np.asarray([2668.5, 1084])) # 69
        self.path_grid.add_edge(60, 69, departments=["F", "G"])
        self.path_grid.add_edge(68, 69, departments=["G"])
        self.path_grid.add_node(np.asarray([2671.5, 1084])) # 70
        self.path_grid.add_edge(69, 70, departments=["G"])
        self.path_grid.add_node(np.asarray([2032, 1577])) # 71
        self.path_grid.add_edge(63, 71, False, departments=["G"])
        self.path_grid.add_node(np.asarray([2190, 1577])) # 72
        self.path_grid.add_edge(65, 72, False, departments=["G"])
        self.path_grid.add_node(np.asarray([2516, 1577])) # 73
        self.path_grid.add_edge(68, 73, False, departments=["G"])
        self.path_grid.add_node(np.asarray([2671.5, 1577])) # 74
        self.path_grid.add_edge(70, 74, False, departments=["G"])
        self.path_grid.add_node(np.asarray([2343, 1730])) # 75
        self.path_grid.add_edge(71, 75, False)
        self.path_grid.add_edge(72, 75, False)
        self.path_grid.add_edge(73, 75, False)
        self.path_grid.add_edge(74, 75, False)

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

        for edge in self.path_grid.sorted_edges["A"]:
            plt.plot([edge.start.pos[0], edge.end.pos[0]], [-edge.start.pos[1], -edge.end.pos[1]], color="b",
                     marker="x", alpha=0.5)
            if edge.bidirectional:
                plt.plot([edge.end.pos[0], edge.start.pos[0]], [-edge.end.pos[1], -edge.start.pos[1]], color="b",
                         marker="x", alpha=0.5)

        plt.show()
