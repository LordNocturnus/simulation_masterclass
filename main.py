import simpy
from src.queuing import createResources
from src.customer_factory import CustomerFactory
import pathlib
import os
from matplotlib import pyplot as plt

# ensure correct cwd
os.chdir(pathlib.Path(__file__).parent)

plt.style.use("ggplot")


# initialize env instance
env = simpy.Environment()

# initialize shared resources
resources = createResources(env, n_shoppingcars=45, n_baskets=300, n_bread=4, n_cheese=3, n_checkouts=4)

print(pathlib.Path(os.getcwd()).joinpath("config.json"))
customer_factory = CustomerFactory(env, pathlib.Path(os.getcwd()).joinpath("config.json"), resources, seed=0)
customer_factory.run()

env.run()


# resources["checkouts"][0].waitTimeHistogram()
# resources["shopping carts"].waitTimeHistogram()
# resources["shopping carts"].useTimeHistogram()

print(resources["shopping carts"].averageWaitTime(), resources["shopping carts"].averageUseTime())
print(resources["baskets"].averageWaitTime(), resources["baskets"].averageUseTime())
print(resources["checkouts"][0].averageWaitTime(), resources["checkouts"][0].averageUseTime())




