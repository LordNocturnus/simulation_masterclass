import pygame as pg
import numpy as np

class Visualization:

    def __init__(self, store, customer_factory, env, scale, margin=0.1):
        self.store = store
        self.customer_factory = customer_factory
        self.env = env
        self.scale = scale
        self.margin = margin

        pg.init()
        self.window_size = np.asarray([800, 600])

        self.gameDisplay = pg.display.set_mode(self.window_size)
        self.surface = pg.surface.Surface(self.window_size, pg.SRCALPHA)
        pg.display.set_caption('Customer position visualization')

        self.black = np.asarray((1, 1, 1))
        self.red = np.asarray((255, 1, 1))
        self.green = np.asarray((1, 255, 1))
        self.blue = np.asarray((1, 1, 255))
        self.white = np.asarray((255, 255, 255))

        self.clock = pg.time.Clock()
        self.ended = False

    def run(self, env):
        while not self.ended:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.ended = True
            self.surface.fill(self.black)
            self.draw_store()
            self.draw_customers()

            self.gameDisplay.blit(self.surface, self.surface.get_rect())
            pg.display.update()
            yield env.timeout(1)
            self.clock.tick(30)
        pg.quit()

    def scale_point(self, point):
        return self.window_size * self.margin + point * self.window_size / self.scale * (1 - 2 * self.margin)

    def draw_store(self):
        for department in self.store.departments.values():
            for shelf in department.shelves:
                pg.draw.line(self.surface, self.red, self.scale_point(shelf.start), self.scale_point(shelf.end))

    def draw_customers(self):
        for c in self.customer_factory.customers:
            if c.draw:
                pg.draw.circle(self.surface, self.blue, self.scale_point(c.pos), 10)
