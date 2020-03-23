from copy import deepcopy
import matplotlib.pyplot as plt
import networkx as nx
from networkx import Graph
import data_loading as dtld
from pathlib import Path


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
    node_sizes = 3
    pos = nx.layout.spring_layout(G)

    # DRAW
    plt.figure()
    nodes = nx.draw_networkx_nodes(G, pos, node_size=node_sizes)
    edges = nx.draw_networkx_edges(G, pos, arrowstyle='->', arrowsize=1, width=1)
    plt.show()


def add_connections(tasks_dict, G):
    '''
    :param tasks_dict: dictionnary of tasks
    :param G: NetworkX Graph
    :return: adds edges to task_dict
    '''
    for task in range(1, len(tasks_dict) + 1):
        try:
            for dep in tasks_dict[task].dependence:
                G.add_edge(dep, task)
        except:
            pass
            # print(f'error in add_connection on task n°{task}')


# TEST LAUNCH
if __name__ == "__main__":
    # graph to use
    data_folder = Path("../graphs")
    path_graph = data_folder / "persoGraph.json"
    tasks_dict = dtld.loadTasks(path_graph)
    keys = sorted(tasks_dict.keys())
    ranges = list(range(keys[0], keys[0] + len(tasks_dict)))
    for i in ranges:
        if i not in keys:
            print(f'{i} is not in tasks keys')

    # tests
    print_plane_graph(tasks_dict)

'''
colormap
nodes = nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color='blue')
edges = nx.draw_networkx_edges(G, pos, node_size=node_sizes, arrowstyle='->', arrowsize=10, edge_color=edge_colors, edge_cmap=plt.cm.Blues, width=2)
'''
