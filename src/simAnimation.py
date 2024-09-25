import pygame
from matplotlib import pyplot as plt
from datetime import timedelta

class simAnimation():
    def __init__(self, sim, run_index=0, window_size = (800, 600), time_scale_anim=1/3600, timestep_sim_seconds = 1):
        self.sim = sim
        self.resources = sim.resourceLog[run_index]
        self.customers = sim.customerLog[run_index]

        # initialize pygame elements
        pygame.init()
        self.window_size = window_size
        self.window = pygame.display.set_mode(window_size)

        # TIME VARIABLES
        self.sim_time = 0 # initialize sim time at zero
        self.sim_timestep = timestep_sim_seconds
        self.sim_end_time = self.customers.simulation_end_time
        self.time_scale_anim = time_scale_anim  # ratio of animation time to simulation time ( default: 1 second / 1 hour)
         # tick steptime for pygame, in miliseconds
        self.time_step_anim_miliseconds = int(timestep_sim_seconds * self.time_scale_anim * 1000)

        self.font = pygame.font.Font('freesansbold.ttf', 32)
        self.colors = {
            'white' : (255, 255, 255),
            'black': (0, 0, 0),
            'green' : (0, 255, 0),
            'blue' : (0, 0, 128)
        }

    def run(self, loopTillQuit = True):
        self.START_TICKS = pygame.time.get_ticks()
        while self.sim_time < self.sim_end_time or loopTillQuit: # run until end time is reached or loop until quit


            self.window.fill(self.colors['white'])  # set background color

            for event in pygame.event.get():
                if event.type == pygame.QUIT: # quit animation if requested
                    pygame.quit()
                    quit()


            self.display_timer() # timer in top-right corner

            #TODO: ADD STUFF TO WINDOW
            #1) departments with text: name of dept, no. of customers inside
            #2) for dept with queues, add queue length(s)
            #3) shopping cart and basket availability and queues
            #4) (optional) running event log
            #5) (very optional) customer movement between departments



            # end-of-loop routine
            pygame.time.delay(self.time_step_anim_miliseconds) # iterate animation time
            self.sim_time += self.sim_timestep

            # reset sim timer once end time reached
            if self.sim_time > self.sim_end_time:
                self.sim_time = 0.0
            pygame.display.update() #update the window view at the end of the loop

    def display_timer(self):
        # TIME WINDOW
        timetext = self.font.render(self.simulation_time_text(),
                                    True,
                                    self.colors['black'],
                                    self.colors['white'])
        timerect = timetext.get_rect()
        self.window.blit(timetext, timerect)

    def simulation_time_text(self):
        sec = 8 * 3600 + self.sim_time # START AT 8 AM => add 8 hours to timer
        td = timedelta(seconds = sec)
        return str(td)



if __name__ == "__main__":
    from src.simulation import Simulation
    import pathlib
    import os
    import json

    # access config file
    # config_path = pathlib.Path(os.getcwd()).joinpath("../debug_config.json")
    config_path = pathlib.Path(os.getcwd()).joinpath("../config.json")
    with open(config_path) as config_p:  # if it's a path, read the file
        config = json.load(config_p)

    # initialize simulation
    ms = Simulation(config, runs=1, overwrite_print=False)
    ms.run()
    sa = simAnimation(ms, timestep_sim_seconds=3600)
    sa.run()



