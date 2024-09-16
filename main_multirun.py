import simpy
from src.queuing import createResources
from src.multisim import MultiSim
from src.customer_factory import CustomerFactory
import pathlib
import os
from matplotlib import pyplot as plt


# ensure correct cwd
os.chdir(pathlib.Path(__file__).parent)

plt.style.use("ggplot")

ms = MultiSim(N_RUNS=10)
ms.run()
ms.plotAvailability("shopping carts")






