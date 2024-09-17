import simpy
from src.queuing import createResources
from src.simulation import Simulation
from src.customer_factory import CustomerFactory
import pathlib
import os
import json
from matplotlib import pyplot as plt


# ensure correct cwd
os.chdir(pathlib.Path(__file__).parent)
plt.style.use("ggplot")

# access config file
config_path = pathlib.Path(os.getcwd()).joinpath("config.json")
with open(config_path) as config_p:  # if it's a path, read the file
    config = json.load(config_p)

ms = Simulation(config, N_RUNS=3)
ms.run()

ms.printResourceUse()
ms.printThroughputData()
ms.plotThroughputHistogram()
ms.plotAvailability("shopping carts")






