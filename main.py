import simpy
from src.queuing import createResources
from src.customer_factory import CustomerFactory
import pathlib
import os
from matplotlib import pyplot as plt

# TODO: replace all placeholders
# TODO: *actually* export and save data (printing doesn't count)
# TODO: postprocessing?

# ensure correct cwd
os.chdir(pathlib.Path(__file__).parent)

plt.style.use("ggplot")


# initialize env instance
env = simpy.Environment()

# initialize shared resources
resources = createResources(env)

print(pathlib.Path(os.getcwd()).joinpath("config.json"))
customer_factory = CustomerFactory(env, pathlib.Path(os.getcwd()).joinpath("config.json"), resources)
customer_factory.run()

env.run()


