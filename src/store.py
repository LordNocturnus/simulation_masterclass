from matplotlib import pyplot as plt
import numpy as np

from src.department import Department
from src.shelf import Shelf


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

        self.scale(np.asarray([2780.0, 1730.0]), np.asarray([40.0, 30.0]))

    def scale(self, old, new):
        # scale each department using old and new extends of the store
        for key in self.departments:
            self.departments[key].scale(old, new)
