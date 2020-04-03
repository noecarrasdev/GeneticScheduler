import ordre
from copy import deepcopy
import matplotlib.pyplot as plt
import networkx as nx
from networkx import Graph
import data_loading as dtld
from pathlib import Path
from matplotlib import cm
from matplotlib.colors import ListedColormap, LinearSegmentedColormap

# CODE

def getpos(tasks_dict):
    '''
    :param tasks_dict: dictionnary of tasks
    :return: a pos object for displaying graphs
    '''

    # GRAPH
    G = Graph()
    n = len(tasks_dict)
    G.add_nodes_from(range(1, n + 1))
    add_connections(tasks_dict, G)

    pos = nx.layout.spring_layout(G)
    return pos


def print_plane_graph(tasks_dict, label=False):
    '''
    :param tasks_dict: dictionnary of tasks
    :return: prints a graph
    '''

    # GRAPH
    G = Graph()
    n = len(tasks_dict)
    G.add_nodes_from(range(1, n + 1))
    add_connections(tasks_dict, G)

    # DRAWING PARAMS
    if n < 1000:
        node_sizes = 40 + 500 * (1000 - n) / 1000
    else:
        node_sizes = 40
    pos = nx.layout.spring_layout(G)

    # DRAW
    plt.figure()
    nx.draw_networkx_nodes(G, pos, node_size=node_sizes)
    nx.draw_networkx_edges(G, pos, arrowstyle='->', arrowsize=2, width=1)
    if label:
        labels = {i + 1: str(i + 1) for i in range(n)}
        nx.draw_networkx_labels(G, pos, labels=labels)
    plt.show()


def add_connections(tasks_dict, G, listrev=None):
    '''
    :param tasks_dict: dictionnary of tasks
    :param G: NetworkX Graph
    :return: adds edges to task_dict
    '''
    for task in range(1, len(tasks_dict) + 1):
        try:
            for dep in tasks_dict[task].dependence:
                if listrev:
                    G.add_edges_from(listrev[dep], listrev[task])
                else:
                    G.add_edge(dep, task)
        except:
            print(f'error in add_connection on task n°{task}')
            pass


def print_color_graph(tasks_dict, ordreprint, label=False, pos=None, title=None):
    '''
    :param tasks_dict: dictionnary of tasks
    :param ordreprint: ordre object or list
    :return: prints a graph
    '''
    # ACCESSING COLORMAPS
    viridis = cm.get_cmap('viridis', 12)

    # ORDRE
    listprint = []
    if type(ordreprint) == type([]):
        n = len(ordreprint)
        listprint = ordreprint
    else:
        ordre_attr = ordreprint.ordre
        n = len(ordre_attr)
        for i in range(n):
            listprint.append(ordre_attr[i])

    # REVERSE THE ORDER TO CREATE THE GRAPH
    # listrev[i] for i in the initial task ranks (issued from the source JSON)
    # gives the position of this node in the order found
    # allows to consruct the graph with the order of nodes
    listrev = [None] * (n + 1)
    for i in range(0, n):
        ind_i = listprint[i]
        listrev[ind_i] = i

    # COLOR
    color_list = [viridis(i / n) for i in range(n)]

    # GRAPH
    G = Graph()
    G.add_nodes_from(listprint)
    add_connections(tasks_dict, G)

    # DRAWING PARAMS
    if n < 1000:
        node_sizes = 40 + 500 * (1000 - n)/1000
    else:
        node_sizes = 40
    # uses own layout if none specified
    if not pos:
        pos = nx.layout.spring_layout(G)

    # DRAW
    plt.figure()
    if title:
        plt.title(title)
    nodes = nx.draw_networkx_nodes(G, pos, node_color=color_list, node_size=node_sizes)
    edges = nx.draw_networkx_edges(G, pos, arrowstyle='->', arrowsize=1, width=1)
    if label:
        labels = {i + 1: str(i + 1) for i in range(n)}
        nx.draw_networkx_labels(G, pos, labels=labels)
    plt.show()



# TEST LAUNCH

if __name__ == "__main__":

    data_folder = Path("../graphs")
    path_graph = data_folder / "persoGraph.json"
    tasks_dict = dtld.loadTasks(path_graph)
    keys = sorted(tasks_dict.keys())
    ordre1 = [i for i in range(1, 11)]
    ordre2 = [1, 3, 6, 2, 4, 5, 10, 7, 8, 9]
    print_color_graph(tasks_dict, ordre2, label=True)
    print_color_graph(tasks_dict, ordre1, label=True)
    print_plane_graph(tasks_dict, label=True)