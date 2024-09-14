from src.queuing import checkoutProcess, breadQueue, cheeseQueue
import numpy.random as rnd

# generic function for the other departments, likely will have to be changed for the next assignment
# TODO:placeholders
def generic_department_function(customer, env, department_id):

    print('{} enters department {}'.format(customer.ucid, department_id))

    for item in range(customer.shopping_list[department_id]):
        t_pick = float(rnd.uniform(20, 30, 1))
        yield env.timeout(t_pick)
        print('{} picks an item at department {} in {:.2f} seconds'.format(customer.ucid, department_id, t_pick))

    print('{} leaves department {}'.format(customer.ucid, department_id))

# wrapper for the queue functions, adding the enter and leave statements!
def department_cd_function(customer, env, department_id):
    print('{} enters department {}'.format(customer.ucid, department_id))

    match department_id:
        case 'C':
            queue = env.process(breadQueue(customer, env, customer.resources['bread clerks']))
        case 'D':
            queue = env.process(cheeseQueue(customer, env, customer.resources['cheese clerks']))

    yield queue

    print('{} leaves department {}'.format(customer.ucid, department_id))

# wrapper for the checkout queue, including pring statements
def checkout_wrapper(customer, env):
    print('{} arrives at checkout'.format(customer.ucid))
    queue = env.process(checkoutProcess(customer, env, customer.resources['checkouts']))
    yield queue
    print('{} leaves the store at {}'.format(customer.ucid, env.now))



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



