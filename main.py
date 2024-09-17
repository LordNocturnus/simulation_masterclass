from src.simulation import Simulation
import pathlib
import os
import json
from matplotlib import pyplot as plt
from scipy.stats import truncnorm
import numpy as np


# ensure correct cwd
os.chdir(pathlib.Path(__file__).parent)
plt.style.use("ggplot")

# access config file
config_path = pathlib.Path(os.getcwd()).joinpath("config.json")
with open(config_path) as config_p:  # if it's a path, read the file
    config = json.load(config_p)

ms = Simulation(config, runs=1)
ms.run()

ms.print_basket_use()
ms.print_cart_use()
ms.print_checkout_use()
ms.print_bread_use()
ms.print_cheese_use()
ms.plot_availability("shopping_carts")#






