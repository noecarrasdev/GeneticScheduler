import numpy as np
import task

def initialisation_rand(graph):
    '''
    :param graph: dict
    :return: a valid combination
    '''

    n = len(graph)
    res = []
    frontier = []

    # gives an image of the actual dependancies
    task_dependancies = []
    for i in range(n):
        # string pour les nombres et appels au dico ?
        task_dependancies.append(graph[f'{i}'].Dependencies)

    # gives task depending of the one searched
    task_todepend = [[] * n]
    for i in range(n):
        for dep in task_dependancies[i]:
            task_todepend[dep].append(i)

    for key in graph.keys():
        if not graph[key].Dependencies:
            frontier.append(key)

    while len(res) < n:
        random_task = np.random.choice(frontier, 1)
        res.append(random_task)
        frontier.remove(random_task)
        for enfant in task_todepend[random_task]:
            task_dependancies[enfant].remove(random_task)
            if task_dependancies[enfant] == []:
                frontier.append(enfant)

    return res


def population_initiale(graph, nombre):
    population = []
    for i in range(nombre):
        population.append(initialisation_rand(graph))
    return population

