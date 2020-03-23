import numpy as np
import task
import time_personalized
import ordre
import data_loading as dtld
from pathlib import Path
from copy import deepcopy


# CODE

def initialisation_rand(graph):
    '''
    :param graph: dict of tasks indeed by integers corresponding to the task.ID attribute
    :return: a valid combination
    '''
    # initial lists
    graph_copy = deepcopy(graph)
    graph_copy2 = deepcopy(graph)
    n = len(graph_copy)
    res = []
    frontier = []

    # gives an image of the actual dependancies, to remove them during the algorithm
    # nb : graphs starts at 0 so in the position [0] we place a None marker
    task_dependencies = [None]
    for i in range(1, n + 1):
        task_dependencies.append(graph_copy[i].dependence)

    # gives tasks depending of the current task
    task_todepend = [[] for i in range(n + 1)]
    for i in range(1, n + 1):
        for dep in task_dependencies[i]:
            task_todepend[dep].append(i)

    # creation de la frontière
    for i in range(1, len(task_dependencies)):
        if not task_dependencies[i]:
            frontier.append(i)

    # ajout progressif des enfants
    while len(res) < n:
        random_task = np.random.choice(frontier, 1)[0]
        res.append(random_task)
        frontier.remove(random_task)
        for enfant in task_todepend[random_task]:
            task_dependencies[enfant].remove(random_task)
            if not task_dependencies[enfant]:
                frontier.append(enfant)

    # transform res into an Ordre object
    res_ordre = ordre.Ordre(np.array([graph_copy2[i] for i in res]))

    if res_ordre.isLegal(n):
        return res_ordre
    else:
        print('non-legal child')
        return None


def population_initiale(graph, nombre):
    '''
    :param graph: dict of tasks indeed by integers corresponding to the task.ID attribute
    :param nombre: number of initialized individuals wanted
    :return: a list of valid Ordre objects
    '''
    population = []
    for _ in range(nombre):
        graph_copy = deepcopy(graph)
        population.append(initialisation_rand(graph_copy))
    return population


# TEST LAUNCH
if __name__ == "__main__":
    # graph to use
    data_folder = Path("../graphs")
    path_graph = data_folder / "smallRandom.json"

    # Load the tasks
    tasks_dict = dtld.loadTasks(path_graph)

    # real initialisation
    first_list = initialisation_rand(tasks_dict)
    print('result is : ', first_list, ', legal ? : ', first_list.isLegal(len(tasks_dict)))

    # batch initialisation
    pop_test = population_initiale(tasks_dict, 10)
    for i in range(10):
        print(pop_test[i], pop_test[i].isLegal(10))