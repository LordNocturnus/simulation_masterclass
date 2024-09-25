import pygame
from matplotlib import pyplot as plt
from datetime import timedelta
import numpy as np


class simAnimation():
    def __init__(self, sim, run_index=0, window_size = (800, 600), time_scale_anim=1/3600, timestep_sim_seconds = 1):
        self.sim = sim
        self.resources = sim.resourceLog[run_index]
        self.customers = sim.customerLog[run_index]
        self.departments = sim.departmentLog[run_index]

        # initialize pygame elements
        pygame.init()
        self.window_size = window_size
        self.window = pygame.display.set_mode(window_size)

        # window margin
        self.margin = 5 # window units

        # TIME VARIABLES
        self.sim_time = 0 # initialize sim time at zero
        self.sim_timestep = timestep_sim_seconds
        self.sim_end_time = self.customers.simulation_end_time
        self.time_scale_anim = time_scale_anim  # ratio of animation time to simulation time ( default: 1 second / 1 hour)
         # tick steptime for pygame, in miliseconds
        self.time_step_anim_miliseconds = int(timestep_sim_seconds * self.time_scale_anim * 1000)

        self.timefont = pygame.font.Font('freesansbold.ttf', 32)
        self.departmentfont = pygame.font.Font('freesansbold.ttf', 16)



        self.colors = {
            'white' : (255, 255, 255),
            'black': (0, 0, 0),
            'green' : (0, 255, 0),
            'blue' : (0, 0, 255),
            'red' : (255, 0, 0)
        }

    def run(self, loopTillQuit = True):
        while self.sim_time < self.sim_end_time or loopTillQuit: # run until end time is reached or loop until quit
            self.window.fill(self.colors['white'])  # set background color
            for event in pygame.event.get():
                if event.type == pygame.QUIT: # quit animation if requested
                    pygame.quit()
                    quit()

            #TODO: ADD STUFF TO WINDOW
            #0) simulation time display
            self.display_timer() # timer in top-right corner

            #1) departments with text: name of dept, no. of customers inside
            #2) for dept with queues, add queue length(s)
            self.display_departments()

            #3) entrance and checkout boxes, with queue lengths and shopping cart/basket availability
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
        timetext = self.timefont.render(self.simulation_time_text(),
                                    True,
                                    self.colors['black'],
                                    self.colors['white'])
        timerect = timetext.get_rect()
        self.window.blit(timetext, (self.margin, self.margin))  # draw text at top-right corner

    def simulation_time_text(self):
        sec = 8 * 3600 + self.sim_time # START AT 8 AM => add 8 hours to timer
        td = timedelta(seconds = sec)
        return str(td)

    def display_departments(self):
        NDEPS = len(self.departments)

        rect_height = self.window_size[1] / (NDEPS + 10) # arbitrary

        xrect = 0 + self.margin
        yrect = rect_height + self.margin

        for key, dep in self.departments.items():

            rect_width = self.department_rect_width(dep)
            rect = pygame.Rect((xrect, yrect), (rect_width, rect_height))
            _ = pygame.draw.rect(self.window, self.colors['red'], rect)

            depttext = self.departmentfont.render(self.department_text(dep),
                                            True,
                                            self.colors['black'],)
            self.window.blit(depttext, (xrect + self.margin, yrect+rect_height/2))

            yrect += rect_height + self.margin


    def department_rect_width(self, dep):
        no_customers = self.get_customers_in_dep(dep)
        base_rect_width = self.window_size[0] / 3 # arbitrary
        size_range = self.window_size[0] - base_rect_width - 2 * self.margin

        return base_rect_width + size_range * (1 - np.exp(- no_customers * 0.1386)) # arbitrary interpolation function

    def department_text(self, dep):
        # render does not support newline characters :))))))))
        no_customers = self.get_customers_in_dep(dep)

        # queue
        if dep.queue is not None:
            queue_length = self.get_queue_length(dep.queue)
            return '{}  | customers: {} | queue length: {}'.format(dep.name, no_customers, queue_length)

        # no queue
        else:
            return '{} | customers: {}'.format(dep.name, no_customers)

    def get_customers_in_dep(self, dep):
        # returns the no. of customers in department dep at time self.simtime
        # wrapper around get_event_cumsum
        return self.get_event_cumsum(dep.log_event, dep.log_time)

    def get_queue_length(self, resource):
        # wrapper around get_event_cumsum
        return self.get_event_cumsum(resource.log_event, resource.log_time)

    def get_event_cumsum(self, log_event, log_time):
        # oneliner extravaganza
        return sum([ind for ind, time in zip(log_event, log_time) if time <= self.sim_time])


    def display_entrance(self):
        # TODO: fill in
        pass

    def display_checkout(self):
        # TODO: fill in
        pass


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
    sa = simAnimation(ms, timestep_sim_seconds=15)
    sa.run()



