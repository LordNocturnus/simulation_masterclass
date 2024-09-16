import simpy
from simpy import Resource
from operator import itemgetter

def createResources(env, n_shoppingcars=45, n_baskets = 300, n_bread=4, n_cheese=3, n_checkouts=4):
    shoppingCarts = Resource(env, capacity=n_shoppingcars)
    baskets = Resource(env, capacity=n_baskets)
    breadClerks = Resource(env, capacity=n_bread)
    cheeseClerks = Resource(env, capacity=n_cheese)

    checkouts = [
        Resource(env, capacity=1) for _ in range(n_checkouts)
    ]

    # return shoppingCarts, baskets, breadClerks, cheeseClerks, checkouts
    return {
        "shopping carts" : shoppingCarts,
        "baskets" : baskets,
        "bread clerks" : breadClerks,
        "cheese clerks" : cheeseClerks,
        "checkouts" : checkouts
    }

def checkoutProcess(customer, env, checkouts):

    #access checkout queues to see which is the quickest
    queue_lengths = [
        len(ch.put_queue) + ch.count for ch in checkouts
    ]

    # find the index of the shortest queue
    index, element = min(enumerate(queue_lengths), key=itemgetter(1))

    # enter the shortest queue
    with checkouts[index].request() as checkout_request:
        if customer.flags["print"]:
            print('{:.2f}: {} enters queue at checkout counter {}'.format(env.now,customer.ucid, index))
        yield checkout_request  # wait to be served
        if customer.flags["print"]:
            print('{:.2f}: {} is served at checkout counter {}'.format(env.now,customer.ucid, index))

        t_tot_scan = 0.
        #scan each item
        for n_item in range(customer.total_items()):
            t_scan = float(customer.rng.normal(customer.stochastics["scan_vars"][0], customer.stochastics["scan_vars"][1], 1))
            t_tot_scan += t_scan
            yield env.timeout(t_scan)

        if customer.flags["print"]:
            print('{:.2f}: {} scans {} items in {:.2f} seconds'.format(env.now,customer.ucid, customer.total_items(), t_tot_scan))

        # payment
        t_pay = float(customer.rng.uniform(customer.stochastics["payment_bounds"][0], customer.stochastics["payment_bounds"][1], 1))
        yield env.timeout(t_pay)

        if customer.flags["print"]:
            print('{:.2f}: {} paid in {:.2f} seconds'.format(env.now,customer.ucid, t_pay))

def breadQueue(customer, env, breadClerks):
    with breadClerks.request() as bread_request:

        if customer.flags["print"]:
            print('{:.2f}: {} enters queue at the bread department'.format(env.now,customer.ucid))
        yield bread_request  # wait to be served

        if customer.flags["print"]:
            print('{:.2f}: {} is served at the bread department'.format(env.now,customer.ucid))

        t_bread = float(customer.rng.normal(customer.stochastics["bread_vars"][0], customer.stochastics["bread_vars"][1], 1))
        yield env.timeout(t_bread)

        if customer.flags["print"]:
            print('{:.2f}: {} received bread item(s) in {:.2f} seconds'.format(env.now,customer.ucid, t_bread))

def cheeseQueue(customer, env, cheeseClerks):
    with cheeseClerks.request() as cheese_request:

        if customer.flags["print"]:
            print('{:.2f}: {} enters queue at the cheese department'.format(env.now,customer.ucid))

        yield cheese_request  # wait to be served
        if customer.flags["print"]:
            print('{:.2f}: {} is served at the cheese department'.format(env.now,customer.ucid))

        t_cheese = float(customer.rng.normal(customer.stochastics["cheese_vars"][0], customer.stochastics["cheese_vars"][1], 1))
        yield env.timeout(t_cheese)

        if customer.flags["print"]:
            print('{:.2f}: {} received cheese item(s) in {:.2f} seconds'.format(env.now,customer.ucid, t_cheese))

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













