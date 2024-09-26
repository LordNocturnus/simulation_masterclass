import pygame
import matplotlib.pyplot as plt
from datetime import timedelta
import numpy as np



class SimAnimation():
    def __init__(self, sim, run_index=0, window_size=(800, 600), fps = 24, timestep_sim_seconds = 1):
        self.sim = sim
        self._run_index = run_index
        self.update_resources()
        self.max_runs = len(self.sim.resourceLog)

        # initialize pygame elements
        pygame.init()
        self.window_size = window_size
        self.window = pygame.display.set_mode(window_size)
        self.surface = pygame.Surface(window_size, pygame.SRCALPHA)

        # window margin
        self.margin = 5 # window units

        # TIME VARIABLES
        self.sim_time = 0 # initialize sim time at zero
        self.sim_timestep = timestep_sim_seconds
        self.sim_end_time = self.customers.simulation_end_time

        self.fps = fps

        # self.time_scale_anim = (1 / fps) / timestep_sim_seconds # ratio of animation time to simulation time ( default: 1 second / 1 hour)
         # tick steptime for pygame, in miliseconds
        # self.time_step_anim_miliseconds = int(timestep_sim_seconds * self.time_scale_anim * 1000)

        self.timefont = pygame.font.Font('freesansbold.ttf', 32)
        self.departmentfont = pygame.font.Font('freesansbold.ttf', 16)
        self.availabilityfont = pygame.font.Font('freesansbold.ttf', 16)
        self.runinfofont = pygame.font.Font('freesansbold.ttf', 32)

        self.colors = {
            'white' : (255, 255, 255),
            'black': (0, 0, 0, 255),
            'green' : (0, 255, 0, 255),
            'blue' : (0, 0, 255, 255),
            'red' : (255, 0, 0, 255)
        }

        departments = self.departments.keys()
        cmap = plt.cm.get_cmap('gist_rainbow', len(departments))
        self.department_colors = {dept: tuple([int(c * 255) for c in cmap(i)]) for i, dept in enumerate(departments)}

        self.bar_color_positive = self.colors['green']
        self.bar_color_negative = self.colors['red']

        self.rectangle_radius = 20

        self.department_ybox = 0
        self.timer_ybox = 0

        self.looped = False # flag set to true if all runs were displayed

    def update_resources(self): # update resources to the current run
        self.resources = self.sim.resourceLog[self.run_index]
        self.customers = self.sim.customerLog[self.run_index]
        self.departments = self.sim.departmentLog[self.run_index]

    @property
    def run_index(self):
        return self._run_index

    @run_index.setter
    def run_index(self, other):
        self._run_index = other
        self.update_resources()


    def run(self, loopTillQuit = True):
        clock = pygame.time.Clock()
        while not self.looped or loopTillQuit: # run until end time is reached or loop until quit
            self.surface.fill(self.colors['white'])  # reset surface
            for event in pygame.event.get():
                if event.type == pygame.QUIT: # quit animation if requested
                    pygame.quit()
                    quit()

            # display run info in top-right corner
            if self.max_runs > 1:
                self.display_run_info()

            # display simulation time in top-left corner
            self.display_timer() # timer in top-right corner

            # display department and resource bars
            self.display_departments()
            self.display_availability_bars()

            # NOT IMPLEMENTED:
            # 1) running resource text log
            # 2) customer movement animation

            # end-of-loop routine
            self.sim_time += self.sim_timestep

            # reset sim timer once end time reached, go to next run if any
            if self.sim_time > self.sim_end_time:
                self.sim_time = 0.0
                if self.run_index == self.max_runs - 1:
                    self.looped = True # flag loop over all runs
                self.run_index = (self.run_index + 1) % self.max_runs # go to the next run

            self.window.blit(self.surface, dest=(0, 0))
            pygame.display.update() #update the window view at the end of the loop

            clock.tick(self.fps)

    def display_timer(self):
        # TIME WINDOW
        timetext = self.timefont.render(self.simulation_time_text(),
                                    True,
                                    self.colors['black'],
                                    self.colors['white'])
        self.surface.blit(timetext, (self.margin, self.margin))  # draw text at top-right corner
        _, htext = timetext.get_size()
        self.timer_ybox = self.margin + htext

    def simulation_time_text(self):
        sec = 8 * 3600 + self.sim_time # START AT 8 AM => add 8 hours to timer
        td = timedelta(seconds = sec)
        return str(td)

    def display_departments(self):

        rect_height = self.window_size[1] / 20

        xrect = 0 + self.margin
        yrect = self.timer_ybox + self.margin + self.window_size[1] / 20

        for key, dep in self.departments.items():

            rect_width = self.department_rect_width(dep)
            rect = pygame.Rect((xrect, yrect), (rect_width, rect_height))
            _ = pygame.draw.rect(self.surface, self.department_colors[key], rect, border_radius=self.rectangle_radius)

            depttext = self.departmentfont.render(self.department_text(dep),
                                            True,
                                            self.colors['black'],)

            _, htext = depttext.get_size()
            shift = (rect_height - htext) / 2
            self.surface.blit(depttext, (xrect + 4 * self.margin, yrect + shift))

            yrect += rect_height + self.margin

        self.department_ybox = yrect


    def department_rect_width(self, dep):
        no_customers = self.get_customers_in_dep(dep)
        base_rect_width = self.window_size[0] / 2 # arbitrary
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
        ymid = self.department_ybox + self.margin + self.window_size[1] / 20
        height = self.window_size[1] / 15
        for _, resource in self.resources.items():
            if not isinstance(resource,list) and resource.name == "Baskets": # checkouts
                    continue

            self.draw_availability_bar(resource, (xmid, ymid), total_width=self.window_size[0] - 2 * self.margin, total_height=height)

            ymid += height + self.margin


    def draw_availability_bar(self, resource, midpoint, total_width=None, total_height = None):
        """
        Draw an availability bar (can be both positive and negative, relative to midpoint)
        """
        if total_width is None:
            total_width = self.window_size[0] - 2 * self.margin

        if total_height is None:
            total_height = self.window_size[1]/10 # arbitrary

        if not isinstance(resource, list):  # checkouts!
            current_availability = resource.capacity - self.get_queue_length(resource)
            rect_width = total_width / 2 * (1 - np.exp(- abs(current_availability) / resource.capacity * 5)) # arbitrary
            resource_name = resource.name
        else:
            total_capacity = sum(r.capacity for r in resource)
            total_queue = sum(self.get_queue_length(r) for r in resource)
            current_availability = total_capacity - total_queue
            rect_width = total_width / 2 * (
                        1 - np.exp(- abs(current_availability) / total_capacity * 5))  # arbitrary
            resource_name = "Checkouts" # AAAAAAAAAAAA


        xrect = midpoint[0] if current_availability > 0 else midpoint[0] - rect_width
        yrect = midpoint[1]

        availtext = self.availabilityfont.render('{} availability: {}'.format(resource_name, current_availability),
                                              True,
                                              self.colors['black'], )

        self.surface.blit(availtext, (midpoint[0] + self.margin, yrect))
        _, htext = availtext.get_size()

        bar_height = max(total_height - htext, 1) # don't go lower than one pixel

        rect = pygame.Rect((xrect, yrect + htext), (rect_width, bar_height))
        if current_availability > 0:
            _ = pygame.draw.rect(self.surface, self.bar_color_positive, rect, border_radius = self.rectangle_radius)
        else:
            _ = pygame.draw.rect(self.surface, self.bar_color_negative, rect, border_radius = self.rectangle_radius)

    def display_run_info(self):
        runinfo = self.runinfofont.render('run {} out of {}'.format(self.run_index, self.max_runs),
                                     True,
                                     self.colors['black'])
        wtext, htext = runinfo.get_size()
        self.surface.blit(runinfo, (self.window_size[0] - wtext - self.margin, self.margin))



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
    sa = SimAnimation(ms, timestep_sim_seconds=60, fps=24)
    sa.run()



