import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation
from simulation import Simulation


class SimAnimation():
    def __init__(self, sim : Simulation):

        self.departments, _ = sim.get_animation_departments()
    def __initialize_scene(self):
        # Create a figure and axis
        fig, ax = plt.subplots()

        ax.set_xlim(0, 4)  # set axis limits
        ax.set_ylim(0, 3)

        ax.set_aspect('equal')
        ax.axis('off')  # Turn off the axes

        # draw departments
        Ndep = len(self.departments)

        anim_departments = []
        for key, dep, in self.departments.items():
            circle = plt.Circle((0, 0), 1, color='blue', alpha=0.2)
            ax.add_artist(circle)
            anim_departments.append(circle)


        return fig, anim_departments

    def update(self, frame, *args):

        for c in args:
            c.set_radius(c.radius*1.01)

        return tuple(args)

    def show(self):
        fig, anim_departments = self.__initialize_scene()

        ani = matplotlib.animation.FuncAnimation(fig=fig, func=self.update, fargs=(anim_departments), frames=40, interval=30)
        plt.show()

if __name__ == "__main__":
    import pathlib
    import os
    import json

    config_path = pathlib.Path(os.getcwd()).joinpath("../config.json")
    with open(config_path) as config_p:  # if it's a path, read the file
        config = json.load(config_p)

    # initialize simulation
    ms = Simulation(config, runs=10, overwrite_print=False)

    simani = SimAnimation(ms)

    simani.show()