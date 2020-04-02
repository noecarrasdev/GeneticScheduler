import numpy as np
import task
import time_personalized
import ordre
import data_loading as dtld
from pathlib import Path
from copy import deepcopy


# CODE

def initialisation_rand(tasks_dict, verbose=False):
    '''
    :param tasks_dict: dict of tasks indeed by integers corresponding to the task.ID attribute
    :return: a valid combination
    '''
    # initial lists
    n = len(tasks_dict.keys())
    res = []
    frontier = []

    # gives an image of the actual dependancies, to remove them during the algorithm
    # nb : graphs starts at 0 so in the position [0] we place a None marker
    task_dependencies = [None]
    for i in range(1, n + 1):
        task_dependencies.append(deepcopy(tasks_dict[i].dependence))

    # gives tasks depending of the current task
    task_todepend = [[] for i in range(n + 1)]
    for i in range(1, n + 1):
        for dep in task_dependencies[i]:
            task_todepend[dep].append(i)

    # monitor
    if verbose:
        print(f'\nInitial lists')
        for i in range(n + 1):
            print(f'individual {i}')
            print(f'backwards dependences : {task_dependencies[i]}')
            print(f'foward dependences : {task_todepend[i]}')

    # creation de la frontière
    for i in range(1, len(task_dependencies)):
        if not task_dependencies[i]:
            frontier.append(i)

    # monitor
    if verbose:
        print('\ninitial fronier is : ')
        for x in frontier:
            print(f'task {tasks_dict[x].ID}')

    # ajout progressif des enfants
    if verbose:
        print('\nThe main initialization loop begins')
    while len(res) < n:
        random_task = np.random.choice(frontier, 1)[0]

        if verbose:
            print(f'\ntask {random_task} is selected, its left dependencies are : {task_dependencies[random_task]}')

        res.append(random_task)
        frontier.remove(random_task)

        if verbose:
            print(f'the current value of the solution is : {res}')
            print(f'removing dependencies from the {len(task_todepend[random_task])} childs')

        for enfant in task_todepend[random_task]:
            task_dependencies[enfant].remove(random_task)
            if not task_dependencies[enfant]:
                frontier.append(enfant)

                if verbose:
                    print(
                        f'the child {enfant} has {task_dependencies[enfant]} dependencies left so it is added to the frontier')

    if verbose:
        print('\n\n\n')

    # transform res into an Ordre object
    res_ordre = ordre.Ordre(np.array(res))
    if verbose:
        for i in range(n):
            print(
                f'res list has {res[i]} and ordre has {res_ordre.ordre[i]}, the difference being : {res_ordre.ordre[i] - res[i]}')

    if verbose:
        print(f'\n\nthe result is : {res_ordre}')
        print('result is legal ? : ', res_ordre.isLegal(tasks_dict, len(tasks_dict)))

    if res_ordre.isLegal(tasks_dict, n):
        return res_ordre
    else:
        print('non-legal child')
        return None



def population_initiale(tasks_dict, nombre):
    '''
    :param tasks_dict: dict of tasks indeed by integers corresponding to the task.ID attribute
    :param nombre: number of initialized individuals wanted
    :return: a list of valid Ordre objects
    '''
    population = []
    for i in range(nombre):
        population.append(initialisation_rand(tasks_dict))
    return population


# TEST LAUNCH

if __name__ == "__main__":
    # graph to use
    data_folder = Path("../graphs")
    path_graph = data_folder / "mediumComplex.json"

    # Load the tasks
    tasks_dict = dtld.loadTasks(path_graph)

    # real initialisation
    first_ordre = initialisation_rand(tasks_dict)

    # batch initialisation
    pop_test = population_initiale(tasks_dict, 10)
    for i in range(10):
        print(pop_test[i].isLegal(len(tasks_dict)))
