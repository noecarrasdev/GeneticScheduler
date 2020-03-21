import numpy as np
import initialisation
import task
import ordre
import data_loading as dtld
import time_personalized
from pathlib import Path


# PARAMETERS

# graph to use
data_folder = Path("../graphs")
path_graph = data_folder / "smallRandom.json"
# sizes
n_population = 10
n_cores = 4
# generation : sum must be equal to n_population
n_selected = 4          # number of individuals kept during the selection
n_mutated = 4
n_crossed = 2
# genetics
mutations_prob = 0.2
nb_mut_max = 4
crossover_bloc_size = (2, 4) # must be inferior to n_tasks
# other with crossovers ?
# execution
epochs = 3


# MAIN CODE

def main_genetics(path_graph, n_population, n_cores, n_selected, n_mutated, n_crossed, mutation_prob, nb_mut_max, crossover_bloc_size, epochs, verbose=True):
    # load datas
    tasks_dict = dtld.loadTasks(path_graph)
    n_tasks = len(tasks_dict)
    optimal_time = dtld.ideal_time(tasks_dict)

    # initial population
    population = initialisation.population_initiale(tasks_dict, n_population)
    scores = ordre.population_eval(population, n_cores, optimal_time)

    # execution
    for epoch in range(epochs):
        new_pop = []
        if verbose:
            print(f'epoch n°{epoch}')
        # selection of the bests
        if verbose:
            best_ordres = ordre.selection_nbest(population, n_selected, scores, verbose=True)
        else:
            best_ordres = ordre.selection_nbest(population, n_selected, scores)
        # mutations
        mutated_ordres = []
        for i in range(n_mutated):
            add_index = np.random.randint(0, n_selected, 1)
            mutated_ordres.append(best_ordres[add_index])
        ordre.mutation_pop(mutated_ordres, mutations_prob, nb_mut_max)
        # crossovers
        cross_ordres = []
        for i in range(n_crossed):
            parents = np.random.randint(0, n_selected, 2)
            bloc_size = np.random.randint(crossover_bloc_size[0], crossover_bloc_size[1])
            cross_ordres.append(ordre.crossover_2_parents(parents[0], parents[1], bloc_size))
        # evaluations
        population = best_ordres + mutated_ordres + cross_ordres
        scores = ordre.population_eval(population, n_cores, optimal_time)

    # log results to the console
    print('\n\n _______________________________RESULTS_______________________________')
    best_result = ordre.selection_nbest(population, scores)
    print(best_result)
    print('Is the best ordre, with a score of : ', ordre.population_eval([best_result], n_cores, optimal_time))
    print('______________________________________________________________________\n\n')

    return best_result


# START ALGO

best_result = main_genetics(path_graph, n_population, n_cores, n_selected, n_mutated, n_crossed, mutations_prob, nb_mut_max, crossover_bloc_size, epochs)


# LARGER TESTS

def test_ordre_small():
    '''
    works with smallRandom and persoGraph
    '''

    # graph to use
    data_folder = Path("../graphs")
    path_graph = data_folder / "smallRandom.json"
    print(path_graph)

    # parameters
    n_population = 10
    mutate_test = False

    # Load the tasks
    tasks_dict = dtld.loadTasks(path_graph)
    optimal_time = dtld.ideal_time(tasks_dict)

    # creation d'ordres pour l'exemple persoGraph.json
    '''
    ordre_arbitrary1 = [1, 2, 3, 4, 5, 6, 7, 10, 8, 9]
    ordre_arbitrary2 = [1, 3, 6, 2, 4, 5, 7, 8, 9, 10]
    '''

    # ordres de départ pour le smallRandom
    ordre_arbitrary1 = [i for i in range(1, 11)]
    ordre_arbitrary2 = [1, 2, 5, 8, 10, 3, 4, 6, 7, 9]

    ordre1 = np.array([tasks_dict[i] for i in ordre_arbitrary1])
    ordre2 = np.array([tasks_dict[i] for i in ordre_arbitrary2])

    test_ordre1 = ordre.Ordre(ordre1)
    test_ordre2 = ordre.Ordre(ordre2)
    test_ordre_empty = ordre.Ordre(np.array([]))
    test_ordre_error = ordre.Ordre([None])  # throws an error, then this ordre becomes an empty one
    test_illegal_order = ordre.Ordre(np.array([1, 2, 8, 5, 10, 3, 4, 6, 7, 9]))

    print(test_ordre1.isLegal(10))
    print(test_ordre2.isLegal(10))
    print(test_illegal_order.isLegal(10))

    # printing
    print(test_ordre1)
    print(test_ordre2)
    print(test_ordre_empty)
    print(test_ordre_error)

    # mutate_out
    print('before the mutation : ', test_ordre1)
    test_ordre3 = test_ordre1.mutation_out()
    print('after the mutation : ', test_ordre3)
    if mutate_test:
        for i in range(10):
            test_ordre3 = test_ordre1.mutation_out()
            if not len(test_ordre3.ordre) == len(test_ordre1.ordre):
                print('ERROR in the test')
        print('test passed')

    # crossover
    test_ordre4 = ordre.crossover_2_parents(test_ordre1, test_ordre2)
    print('child from the 2 first orders : ', test_ordre4)

    # CPU scheduling and loss function
    time_taken_1_4, CpuOrder14 = test_ordre1.CPUScheduling(4)
    time_taken_2_4, CpuOrder24 = test_ordre2.CPUScheduling(4)
    time_taken_1_2, CpuOrder12 = test_ordre1.CPUScheduling(2)
    print('times taken by 1_4 : ', time_taken_1_4)
    print('times taken by 2_4 : ', time_taken_2_4)
    print('times taken by 1_2 : ', time_taken_1_2)

    print(ordre.print_cpuord(CpuOrder12))
    print(ordre.print_cpuord(CpuOrder14))
    print(ordre.print_cpuord(CpuOrder24))

    ratio_1_4 = time_personalized.metric_ratio(time_taken_1_4, optimal_time) * 4
    print(ratio_1_4)
    ratio_2_4 = time_personalized.metric_ratio(time_taken_1_4, optimal_time) * 4
    print(ratio_2_4)
    ratio_1_2 = time_personalized.metric_ratio(time_taken_1_4, optimal_time) * 2
    print(ratio_1_2)


def test_init_loss():
    '''
    test of the loss function on bigger graphs
    '''

    # graph to use
    data_folder = Path("../graphs")
    path_graph = data_folder / "mediumRandom.json"
    print(path_graph)

    # Load the tasks
    tasks_dict = dtld.loadTasks(path_graph)
    optimal_time = dtld.ideal_time(tasks_dict)

    # parameters
    n_tasks = len(tasks_dict)
    n_pop = 10
    n_cores = 4

    # initial population batch
    population = initialisation.population_initiale(tasks_dict, n_pop)
    for ind in population:
        print(ind)

    # scores of the population:
    scores = []
    for ind in population:
        time_curr, Cpu_curr = ind.CPUScheduling(n_cores)
        scores.append(n_cores * time_personalized.metric_ratio(time_curr, optimal_time))
    print(scores)
