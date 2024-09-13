import simpy
from simpy import Resource
from operator import itemgetter
import numpy.random as rnd

def createResources(env):
    # PLACEHOLDER VALUES
    # TODO:replace placeholders

    shoppingCarts = Resource(env, capacity=45)
    baskets = Resource(env, capacity=300)
    breadClerks = Resource(env, capacity=4)
    cheeseClerks = Resource(env, capacity=3)

    checkouts = [
        Resource(env, capacity=1) for _ in range(4)
    ]

    return shoppingCarts, baskets, breadClerks, cheeseClerks, checkouts

def checkoutProcess(customer, env, checkouts):
    #access checkout queues to see which is the quickest
    queue_lengths = [
        len(ch.put_queue) for ch in checkouts
    ]

    # find the index of the shortest queue
    index, element = min(enumerate(queue_lengths), key=itemgetter(1))

    # enter the shortest queue
    checkout_request = checkouts[index].request()
    yield checkout_request  # wait to be served

    #scan each item
    # TODO:replace placeholders!!!
    for n_item in customer.total_items:
        env.timeout(rnd.normal(1.1, 1.1*0.1, 1))
        print('scanned item {} for customer {}'.format(n_item, customer.id))

    # payment
    env.timeout(rnd.normal(1.1, 1.1 * 0.1, 1))











if __name__ == "__main__":

    env = simpy.Environment(0.0)

    shoppingCarts, baskets, breadClerks, cheeseClerks, checkouts = createResources(env)

    def checkout_user(env, checkoutCounter):
        req = checkoutCounter.request()
        yield req
        yield env.timeout(1)
        checkoutCounter.release(req)
        print(checkoutCounter.put_queue)

    users = [env.process(checkout_user(env, checkouts[0])) for _ in range(10)]
    env.run()



# customer arrives at entrance
# if Customer needs a shopping cart, create a request statement
# shoppingCarts.request()













