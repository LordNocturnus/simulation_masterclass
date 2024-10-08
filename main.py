from src.simulation import Simulation
from src.store import Store
from src.simAnimation import SimAnimation
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
config_path = pathlib.Path(os.getcwd()).joinpath("config.json")
with open(config_path) as config_p:  # if it's a path, read the file
    config = json.load(config_p)

#initialize simulation
ms = Simulation(config, runs=1, overwrite_print=False, visualization=True)

ms.run()#"""

#sa = SimAnimation(ms, timestep_sim_seconds=60, fps=30, window_size=(1080, 720))
#sa.run()

# show results
ms.print_all_resource_uses()
ms.print_store_time()
ms.plot_availability("shopping_carts", save=True)
ms.plot_store_time_vs_start_time(save=True)
ms.plot_availability("C", save=True)
ms.plot_store_time_histogram(n_bins=100, save=True)






