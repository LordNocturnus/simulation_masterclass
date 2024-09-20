from src.simulation import Simulation
import pathlib
import os
import json
from matplotlib import pyplot as plt
from scipy.stats import truncnorm
import numpy as np


# ensure correct cwd
os.chdir(pathlib.Path(__file__).parent)
if "plots" not in os.listdir(os.getcwd()):
    os.makedirs(pathlib.Path(os.getcwd()).joinpath("plots"))
plt.style.use("ggplot")

# access config file
config_path = pathlib.Path(os.getcwd()).joinpath("config.json")
with open(config_path) as config_p:  # if it's a path, read the file
    config = json.load(config_p)

#initialize simulation
ms = Simulation(config, runs=10, overwrite_print=False)

ms.run()

# show results
ms.print_all_resource_uses()
ms.print_store_time()
ms.plot_availability("shopping_carts", save=True)
ms.plot_store_time_vs_start_time(save=True)
ms.plot_availability("C", save=True)
ms.plot_store_time_histogram(n_bins=100, save=True)







