import pygame
from matplotlib import pyplot as plt


class simAnimation():
    def __init__(self, sim, run_index=0, window_size = (800, 600), time_scale=1/3600, timestep_sim_s = 1):
        self.sim = sim
        self.resources = sim.resourceLog[run_index]
        self.customers = sim.customerLog[run_index]

        # initialize pygame elements
        pygame.init()
        self.window_size = window_size
        self.window = pygame.display.set_mode(window_size)

        self.END_TIME = self.customers.simulation_end_time
        self.TIME_SCALE = time_scale # by default, animation takes 12 seconds (1 sec in anim time - 1 hour in sim time)
        self.END_TICKS = int(self.END_TIME * self.TIME_SCALE) # end tick for pygame
        self.TIME_STEP_MS = int(timestep_sim_s * self.TIME_SCALE * 1000) # tick steptime for pygame, in miliseconds


        self.font = pygame.font.Font('freesansbold.ttf', 32)
        self.colors = {
            'white' : (0, 0, 0),
            'green' : (0, 255, 0),
            'blue' : (0, 0, 128)
        }

    def run(self):

        timetext = self.font.render('time: {:.2f}'.format(pygame.time.get_ticks() / self.TIME_SCALE),
                                    True,
                                    self.colors['green'],
                                    self.colors['blue'])
        timerect = timetext.get_rect()

        while pygame.time.get_ticks() <= self.END_TICKS: # run until end tick is reached
            pygame.time.delay(self.TIME_STEP_MS) # iterate animation time
            self.window.fill(self.colors['white'])  # set background color

            for event in pygame.event.get():
                if event.type == pygame.QUIT: # quit animation if requested
                    pygame.quit()
                    quit()

            self.window.blit(timetext, timerect)


            #TODO: ADD STUFF

            pygame.display.update() #update the window view at the end of the loop


if __name__ == "__main__":
    from src.simulation import Simulation
    import pathlib
    import os
    import json

    # access config file
    config_path = pathlib.Path(os.getcwd()).joinpath("../debug_config.json")
    with open(config_path) as config_p:  # if it's a path, read the file
        config = json.load(config_p)

    # initialize simulation
    ms = Simulation(config, runs=1, overwrite_print=False)
    ms.run()
    sa = simAnimation(ms)
    sa.run()



