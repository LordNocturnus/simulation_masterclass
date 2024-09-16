from src.queuing import checkoutProcess, breadQueue, cheeseQueue

# generic function for the other departments, likely will have to be changed for the next assignment
def generic_department_function(customer, env, department_id):
    if customer.flags["print"]:
        print('{} enters department {}'.format(customer.ucid, department_id))

    for item in range(customer.shopping_list[department_id]):
        t_pick = float(customer.rng.uniform(customer.stochastics["search_bounds"][0],customer.stochastics["search_bounds"][1], 1))
        yield env.timeout(t_pick)
        if customer.flags["print"]:
            print('{} picks an item at department {} in {:.2f} seconds'.format(customer.ucid, department_id, t_pick))
    if customer.flags["print"]:
        print('{} leaves department {}'.format(customer.ucid, department_id))

# wrapper for the queue functions, adding the enter and leave statements!
def department_cd_function(customer, env, department_id):
    if customer.flags["print"]:
        print('{} enters department {}'.format(customer.ucid, department_id))

    match department_id:
        case 'C':
            queue = env.process(breadQueue(customer, env, customer.resources['bread clerks']))
        case 'D':
            queue = env.process(cheeseQueue(customer, env, customer.resources['cheese clerks']))

    yield queue

    if customer.flags["print"]:
        print('{} leaves department {}'.format(customer.ucid, department_id))

# wrapper for the checkout queue, including pring statements
def checkout_wrapper(customer, env):
    if customer.flags["print"]:
        print('{} arrives at checkout'.format(customer.ucid))
    queue = env.process(checkoutProcess(customer, env, customer.resources['checkouts']))
    yield queue

    if customer.flags["print"]:
        print('{} leaves the store at {:.2f}'.format(customer.ucid, env.now))



# ugh
function_dict = {
    'A': generic_department_function,
    'B': generic_department_function,
    'C': department_cd_function,
    'D': department_cd_function,
    'E': generic_department_function,
    'F': generic_department_function,
    'G': generic_department_function
}



