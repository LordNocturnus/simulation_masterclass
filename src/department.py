from src.queuing import checkoutProcess, breadQueue, cheeseQueue
import numpy.random as rnd

# generic function for the other departments, likely will have to be changed for the next assignment
# TODO:placeholders
def generic_department_function(customer, env, department_id):

    print('customer {} enters department {}'.format(customer.ucid, department_id))

    for item in range(customer.shopping_list[department_id]):
        t_pick = rnd.uniform(20, 30, 1)
        yield env.timeout(t_pick)
        print('customer {} picks an item at department {} in {} seconds'.format(customer.ucid, department_id, t_pick))

    print('customer {} leaves department {}'.format(customer.ucid, department_id))

# wrapper for the queue functions, adding the enter and leave statements!
def department_cd_function(customer, env, department_id):
    print('customer {} enters department {}'.format(customer.ucid, department_id))

    match department_id:
        case 'c':
            breadQueue(customer, env, customer.resources['bread clerks'])
        case 'd':
            cheeseQueue(customer, env, customer.resources['cheese clerks'])

    print('customer {} leaves department {}'.format(customer.ucid, department_id))

# wrapper for the checkout queue, including pring statements
def checkout_wrapper(customer, env):
    print('customer {} arrives at checkout'.format(customer.ucid))
    checkoutProcess(customer, env, customer.resources['checkouts'])
    print('customer {} leaves the store'.format(customer.ucid))



# ugh
function_dict = {
    'a' : generic_department_function,
    'b' : generic_department_function,
    'c' : department_cd_function,
    'd' : department_cd_function,
    'e' : generic_department_function,
    'f' : generic_department_function,
    'g' : generic_department_function
}



