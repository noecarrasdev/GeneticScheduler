from copy import deepcopy
import matplotlib.pyplot as plt
import networkx as nx
from networkx import Graph


# CODE

def print_plane_graph(tasks_dict):
    '''
    :param tasks_dict: dictionnary of tasks
    :return: prints a graph
    '''
    # GRAPH
    G = Graph()
    G.add_nodes_from(range(1, len(tasks_dict) + 1))
    add_connections(tasks_dict, G)

    # DRAWING PARAMS
    node_sizes = [3 + 10 * i for i in range(len(G))]
    pos = nx.layout.spring_layout(G)


    # DRAW
    plt.figure()
    nodes = nx.draw_networkx_nodes(G, pos, node_size=node_sizes)
    edges = nx.draw_networkx_edges(G, pos, node_size=node_sizes, arrowstyle='->', arrowsize=10, width=2)
    plt.show()


def add_connections(tasks_dict, G):
    '''
    :param tasks_dict: dictionnary of tasks
    :param G: NetworkX Graph
    :return: adds edges to task_dict
    '''
    for task in range(1, len(tasks_dict) + 1):
        for dep in tasks_dict[task].dependence:
            G.add_edge(dep, task)


# TEST IN THE MAIN FILE

'''
nodes = nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color='blue')
edges = nx.draw_networkx_edges(G, pos, node_size=node_sizes, arrowstyle='->', arrowsize=10, edge_color=edge_colors, edge_cmap=plt.cm.Blues, width=2)
'''