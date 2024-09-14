import simpy
from src.queuing import createResources
from src.customer import Customer
from src.customer_factory import CustomerFactory
import numpy.random as rnd
import pathlib
import os
from matplotlib import pyplot as plt

# ensure correct cwd
os.chdir(pathlib.Path(__file__).parent)

plt.style.use("ggplot")


# initialize env instance
env = simpy.Environment()

# initialize shared resoures
resources = createResources(env)

print(pathlib.Path(os.getcwd()).joinpath("config.json"))
customer_factory = CustomerFactory(env, pathlib.Path(os.getcwd()).joinpath("config.json"))
customer_factory.run()

env.run()


