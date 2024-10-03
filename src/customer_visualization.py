import pygame as pg
import numpy as np
import datetime

class Visualization:

    def __init__(self, store, customer_factory, env, scale, margin=0.1, customer_size=5):
        self.store = store
        self.customer_factory = customer_factory
        self.env = env
        self.scale = scale
        self.margin = margin
        self.customer_size = customer_size

        pg.init()
        self.window_size = np.asarray([800, 600])

        self.image = pg.transform.scale(pg.image.load('blankstore.png'), self.window_size * (1 - 2 * margin))

        self.gameDisplay = pg.display.set_mode(self.window_size)
        self.surface = pg.surface.Surface(self.window_size, pg.SRCALPHA)
        pg.display.set_caption('Customer position visualization')

        self.font = pg.font.SysFont('Arial', 20)

        self.black = np.asarray((1, 1, 1))
        self.red = np.asarray((255, 1, 1))
        self.green = np.asarray((1, 255, 1))
        self.blue = np.asarray((1, 1, 255))
        self.white = np.asarray((255, 255, 255))

        self.clock = pg.time.Clock()
        self.ended = False

    def run(self, env):
        # run as part of the simpy simulation to "synchronize" the clocks
        while not self.ended:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.ended = True
            self.surface.fill(self.black)
            self.draw_store()
            self.draw_clock(env)
            self.draw_customers(env)

            self.gameDisplay.blit(self.surface, self.surface.get_rect())
            pg.display.update()
            yield env.timeout(60)
            self.clock.tick(60)
            print(self.clock.get_fps())
        pg.quit()

    def scale_point(self, point):
        return self.window_size * self.margin + point * self.window_size / self.scale * (1 - 2 * self.margin)

    def draw_store(self):
        self.surface.blit(self.image, (self.scale_point(0.0), self.scale_point(0.0)))
        for department in self.store.departments.values():
            for shelf in department.shelves:
                pg.draw.line(self.surface, self.red, self.scale_point(shelf.start), self.scale_point(shelf.end))

    def draw_customers(self, env):
        customer_in_store = False
        for c in self.customer_factory.customers:
            if c.draw:
                customer_in_store = True
                if c.basket:
                    pg.draw.circle(self.surface, c.color, self.scale_point(c.pos), self.customer_size)
                else:
                    pg.draw.rect(self.surface, c.color, (self.scale_point(c.pos)[0] - self.customer_size,
                                                           self.scale_point(c.pos)[1] - self.customer_size,
                                                           2 * self.customer_size, 2 * self.customer_size))
        if env.now >= 12.25 * 3600 and not customer_in_store:
            # no more customers in the store terminate
            # checking after 12.25h instead of 12h to prevent customer entering at exactly 20:00 breaking the visualization
            self.ended = True


    def draw_clock(self, env):
        self.surface.blit(self.font.render(str(datetime.timedelta(seconds=8 * 3600 + env.now)), True, self.white), (0, 0) )

