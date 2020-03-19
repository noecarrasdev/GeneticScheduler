import numpy as np
import node

def initialisation_rand(graph):
    '''
    :param graph: dict
    :return: a valid combination
    '''

    n = len(graph)
    res = []
    frontier = []

    # gives an image of the actual dependancies
    node_dependancies = []
    for i in range(n):
        # string pour les nombres et appels au dico ?
        node_dependancies.append(graph[f'{i}'].Dependencies)

    # gives node depending of the one searched
    node_todepend = [[] * n]
    for i in range(n):
        for dep in node_dependancies[i]:
            node_todepend[dep].append(i)

    for key in graph.keys():
        if not graph[key].Dependencies:
            frontier.append(key)

    while len(res) < n:
        random_node = np.random.choice(frontier, 1)
        res.append(random_node)
        frontier.remove(random_node)
        for enfant in node_todepend[random_node]:
            node_dependancies[enfant].remove(random_node)
            if node_dependancies[enfant] == []:
                frontier.append(enfant)

    return res


def population_initiale(graph, nombre):
    population = []
    for i in range(nombre):
        population.append(initialisation_rand(graph))
    return population

