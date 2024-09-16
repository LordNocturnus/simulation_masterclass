import simpy
from src.queuing import createResources, queue_length, plot_queue_length, plot_multiple
from src.customer_factory import CustomerFactory
import pathlib
import os
from matplotlib import pyplot as plt


# ensure correct cwd
os.chdir(pathlib.Path(__file__).parent)

plt.style.use("ggplot")

N_RUNS = 10

logs = {
    "shopping carts" : [],
    "baskets" : [],
    "bread" : [],
    "cheese" : [],
    "checkouts" : [[] for i in range(4)],
}


for i in range(N_RUNS):
    # initialize env instance
    env = simpy.Environment()

    # initialize shared resources
    resources = createResources(env, n_shoppingcars=45, n_baskets=300, n_bread=4, n_cheese=3, n_checkouts=4)

    print(pathlib.Path(os.getcwd()).joinpath("config.json"))
    customer_factory = CustomerFactory(env, pathlib.Path(os.getcwd()).joinpath("config.json"), resources, seed=i)
    customer_factory.run()

    env.run()

    logs["shopping carts"].append(resources["shopping carts"].log)
    logs["bread"].append(resources["bread clerks"].log)
    for i in range(4):
        logs["checkouts"][i].append(resources["checkouts"][i].log)




