import simpy
from src.queuing import createResources
from src.customer import Customer
import numpy.random as rnd

# initialize env instance
env = simpy.Environment(0.0)
# initialize shared resoures
resources = createResources(env)

# add customer factory!
# TODO:add customer factory

# sample customers (replace before submitting!)
customers = [
        Customer(env, resources,
                 {'a' : 1, 'b' : 2, 'c' : 3,'d' : 4, 'e' : 5, 'f' : 6, 'g' : 7},
                 rnd.randint(0, 2, dtype=int), 'abcdefg',
                 rnd.uniform(0, 12*60*60, 1), i) for i in range(1000)
    ]


env.run()


