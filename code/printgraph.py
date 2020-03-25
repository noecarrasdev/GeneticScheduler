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
    nx.draw_networkx_nodes(G, pos, node_size=node_sizes)
    nx.draw_networkx_edges(G, pos, arrowstyle='->', arrowsize=2, width=1)
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
            print(f'error in add_connection on task n°{task}')
            pass


def print_color_graph(tasks_dict, ordreprint):
    '''
    :param tasks_dict: dictionnary of tasks
    :param ordreprint: ordre object
    :return: prints a graph
    '''
    # ACCESSING COLORMAPS
    viridis = cm.get_cmap('viridis', 12)

    # ORDRE AND COLOR
    listprint = []
    ordre_attr = ordreprint.ordre
    n = len(ordre_attr)
    for i in range(n):
        listprint.append(ordre_attr[i].ID)
    color_list = [viridis(i / n) for i in range(n)]

    # GRAPH
    G = Graph()
    G.add_nodes_from(range(1, len(tasks_dict) + 1))
    add_connections(tasks_dict, G)

    # DRAWING PARAMS
    node_sizes = 5
    pos = nx.layout.spring_layout(G)

    # DRAW
    plt.figure()
    nodes = nx.draw_networkx_nodes(G, pos, nodelist=listprint, node_color=color_list, node_size=node_sizes)
    # TODO : vérifier que ça fait pas juste l'ordre de 1 à n mais bien l'ordre donnée pour les couleurs
    edges = nx.draw_networkx_edges(G, pos, arrowstyle='->', arrowsize=1, width=1)
    plt.show()



# TEST LAUNCH

if __name__ == "__main__":
    # graph to use
    data_folder = Path("../graphs")
    path_graph = data_folder / "persoGraph.json"
    tasks_dict = dtld.loadTasks(path_graph)
    keys = sorted(tasks_dict.keys())


'''
colormap
nodes = nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color='blue')
edges = nx.draw_networkx_edges(G, pos, node_size=node_sizes, arrowstyle='->', arrowsize=10, edge_color=edge_colors, edge_cmap=plt.cm.Blues, width=2)
'''
