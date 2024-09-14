from matplotlib import pyplot as plt
import numpy as np
import simpy
import pathlib
import os

from src.customer_factory import CustomerFactory

# ensure correct cwd
os.chdir(pathlib.Path(__file__).parent)

plt.style.use("ggplot")

env = simpy.Environment()
print(pathlib.Path(os.getcwd()).joinpath("config.json"))
customer_factory = CustomerFactory(env, pathlib.Path(os.getcwd()).joinpath("config.json"))
customer_factory.run()
env.run()
