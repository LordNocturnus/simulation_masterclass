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
        len(ch.put_queue) + ch.count for ch in checkouts
    ]

    # find the index of the shortest queue
    index, element = min(enumerate(queue_lengths), key=itemgetter(1))

    # enter the shortest queue
    with checkouts[index].request() as checkout_request:
        print('customer {} enters queue at checkout counter {}'.format(customer.ucid, index))
        yield checkout_request  # wait to be served
        print(
            'customer {} is served at checkout counter {}'.format(customer.ucid, index)
        )

        #scan each item
        # TODO:replace placeholders!!!
        for n_item in range(customer.total_items()):
            t_scan = rnd.normal(1.1, 1.1*0.1, 1)
            yield env.timeout(t_scan)
            print('scanned item {} for customer {} in {} seconds'.format(n_item, customer.ucid, t_scan))

        # payment
        t_pay = rnd.uniform(40, 60, 1)
        yield env.timeout(t_pay)
        print('customer {} paid in {} seconds'.format(customer.ucid, t_pay))

def breadQueue(customer, env, breadClerks):
    with breadClerks.request() as bread_request:
        print('customer {} enters queue at the bread department {}'.format(customer.ucid))
        yield bread_request  # wait to be served
        print(
            'customer {} is served at the bread department {}'.format(customer.ucid)
        )

        t_bread = rnd.normal(120.0, 120.0*0.1, 1)
        yield env.timeout(t_bread)
        print('customer {} received bread item(s) in {} seconds'.format(customer.ucid, t_bread))

def breadQueue(customer, env, cheeseClerks):
    with cheeseClerks.request() as cheese_request:
        print('customer {} enters queue at the cheese department {}'.format(customer.ucid))
        yield cheese_request  # wait to be served
        print(
            'customer {} is served at the cheese department {}'.format(customer.ucid)
        )

        t_cheese = rnd.normal(60.0, 60.0*0.1, 1)
        yield env.timeout(t_cheese)
        print('customer {} received cheese item(s) in {} seconds'.format(customer.ucid, t_cheese))


if __name__ == "__main__":



    from customer import Customer
    env = simpy.Environment(0.0)

    shoppingCarts, baskets, breadClerks, cheeseClerks, checkouts = createResources(env)

    customers = [
        Customer(env, {'hello':10}, 1, 'str', i*10, i) for i in range(50)
    ]

    users = [env.process(checkoutProcess(customer, env, checkouts)) for customer in customers]
    env.run()



# customer arrives at entrance
# if Customer needs a shopping cart, create a request statement
# shoppingCarts.request()













