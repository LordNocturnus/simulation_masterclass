import pygame
from matplotlib import pyplot as plt
from datetime import timedelta
import numpy as np


class simAnimation():
    def __init__(self, sim, run_index=0, window_size=(800, 600), time_scale_anim=1/3600, timestep_sim_seconds = 1):
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
        self.availabilityfont = pygame.font.Font('freesansbold.ttf', 12)




        self.colors = {
            'white' : (255, 255, 255),
            'black': (0, 0, 0),
            'green' : (0, 255, 0),
            'blue' : (0, 0, 255),
            'red' : (255, 0, 0)
        }

        self.department_ybox = 0

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
            self.display_availability_bars()

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
        self.window.blit(timetext, (self.margin, self.margin))  # draw text at top-right corner

    def simulation_time_text(self):
        sec = 8 * 3600 + self.sim_time # START AT 8 AM => add 8 hours to timer
        td = timedelta(seconds = sec)
        return str(td)

    def display_departments(self):
        NDEPS = len(self.departments)

        rect_height = self.window_size[1] / 20

        xrect = 0 + self.margin
        yrect = rect_height + self.margin

        for key, dep in self.departments.items():

            rect_width = self.department_rect_width(dep)
            rect = pygame.Rect((xrect, yrect), (rect_width, rect_height))
            _ = pygame.draw.rect(self.window, self.colors['blue'], rect)

            depttext = self.departmentfont.render(self.department_text(dep),
                                            True,
                                            self.colors['black'],)
            self.window.blit(depttext, (xrect + self.margin, yrect+rect_height/2))

            yrect += rect_height + self.margin

        self.department_ybox = yrect


    def department_rect_width(self, dep):
        no_customers = self.get_customers_in_dep(dep)
        base_rect_width = self.window_size[0] / 3 # arbitrary
        size_range = self.window_size[0] - base_rect_width - 2 * self.margin

        return base_rect_width + size_range * (1 - np.exp(-no_customers * 0.1386)) # arbitrary interpolation function

    def department_text(self, dep):
        # render does not support newline characters :))))))))
        no_customers = self.get_customers_in_dep(dep)

        # queue
        if dep.queue is not None:
            queue_length = self.get_queue_length(dep.queue)
            return '{}  | customers: {} | including queue: {}'.format(dep.name, no_customers, queue_length)

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

    def display_availability_bars(self):

        xmid = self.window_size[0] * 1/2
        ymid = self.department_ybox + self.margin
        height = self.window_size[1] / 20
        for _, resource in self.resources.items():
            if isinstance(resource,
                          list): # checkouts!
                continue
            self.draw_availability_bar(resource, (xmid, ymid), total_width=self.window_size[0] - 2 * self.margin, total_height=height)

            ymid += height + self.margin

        for r in self.resources['checkout']:
            self.draw_availability_bar(r, (xmid, ymid),
                                       total_width=self.window_size[0] - 2 * self.margin, total_height=height)

            ymid += height + self.margin


    def draw_availability_bar(self, resource, midpoint, total_width=None, total_height = None):
        """
        Draw an availability bar (can be both positive and negative, relative to midpoint)
        """
        if total_width is None:
            total_width = self.window_size[0] - 2 * self.margin

        if total_height is None:
            total_height = self.window_size[1]/10 # arbitrary


        current_availability = resource.capacity - self.get_queue_length(resource)

        rect_width = total_width / 2 * (1 - np.exp(- abs(current_availability) / resource.capacity * 5)) # arbitrary
        xrect = midpoint[0] if current_availability > 0 else midpoint[0] - rect_width
        yrect = midpoint[1]

        availtext = self.availabilityfont.render('{} availability: {}'.format(resource.name, current_availability),
                                              True,
                                              self.colors['black'], )

        self.window.blit(availtext, (midpoint[0] + self.margin, yrect))
        _, htext = availtext.get_size()

        bar_height = max(total_height - htext, 1) # don't go lower than one pixel

        rect = pygame.Rect((xrect, yrect + htext), (rect_width, bar_height))
        if current_availability > 0:
            _ = pygame.draw.rect(self.window, self.colors['green'], rect)
        else:
            _ = pygame.draw.rect(self.window, self.colors['red'], rect)


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



