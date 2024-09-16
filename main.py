import simpy
from src.queuing import createResources, queue_length, plot_queue_length, plot_multiple
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

# print(customer_factory.average_wait_time())
# plot_queue_length(resources["shopping carts"].queueLog)
# plot_queue_length(resources["baskets"].queueLog)
# plot_queue_length(resources["bread clerks"].queueLog)
# plot_queue_length(resources["cheese clerks"].queueLog)


plot_multiple(resources["shopping carts"].logs)



