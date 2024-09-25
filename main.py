from src.simulation import Simulation
from src.store import Store
import pathlib
import os
import json
from matplotlib import pyplot as plt
import numpy as np


# ensure correct cwd
os.chdir(pathlib.Path(__file__).parent)
if "plots" not in os.listdir(os.getcwd()):
    os.makedirs(pathlib.Path(os.getcwd()).joinpath("plots"))
plt.style.use("ggplot")

# access config file
config_path = pathlib.Path(os.getcwd()).joinpath("debug_config.json")
with open(config_path) as config_p:  # if it's a path, read the file
    config = json.load(config_p)

"""#initialize simulation
ms = Simulation(config, runs=1)

ms.run()#"""

"""# show results
ms.print_all_resource_uses()
ms.print_store_time()
ms.plot_availability("shopping_carts")
ms.plot_store_time_vs_start_time()
ms.plot_availability("C")
ms.plot_store_time_histogram(n_bins=100)#"""

test = Store(None, config)
test.plot()






