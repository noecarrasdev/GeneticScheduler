import numpy as np
import initialisation
import task
import ordre
import data_loading as dtld
import time_personalized
from pathlib import Path
import analysis
import printgraph
from time import time


# PARAMETERS

# graph to use
data_folder = Path("../graphs") 
path_graph = data_folder / "smallRandom.json"
#path_graph = "smallComplex.json"

# sizes
n_population = 10
n_cores = 4
# generation : sum must be equal to n_population
# n_selected is the number of best individuals kept between each iteration, same idea for n_mutated and n_crossed
n_selected = 3
n_mutated = 4
n_crossed = 3
# genetics --> adapt the blocs size and the mutation numbers to the number of tasks
mutations_prob = 0.6
nb_mut_max = 10
crossover_bloc_size = (1, 7) # must be inferior to n_tasks
# execution
epochs = 10
# logs during the execution?
verbose = True
time_analytics = True
colored_graph_displaying = True
verify_legality = False
graph_evolution = False


# MAIN CODE

def main_genetics(path_graph, n_population, n_cores, n_selected, n_mutated, n_crossed, mutation_prob, nb_mut_max, crossover_bloc_size, epochs, verbose=True, time_analytics=True, colored_graph_displaying=True, verify_legality=False, graph_evolution=False):
    '''
    Main call function that starts the genetic algorithm
    '''
    # load datas
    tasks_dict = dtld.loadTasks(path_graph)
    n_tasks = len(tasks_dict.keys())
    optimal_time = dtld.ideal_time(tasks_dict)

    # initial population
    population = initialisation.population_initiale(tasks_dict, n_population)
    scores = ordre.population_eval(population, n_cores, tasks_dict, optimal_time)

    # time_analytics
    ana_ordres = []
    ana_scores = []
    ana_means = []

    # graph evolution
    graph_evo_best = []

    # execution
    for epoch in range(epochs):
        if verbose:
            print(f'\n_________________________epoch n{epoch}__________________________')
        # selection of the bests
        if verbose:
            best_ordres = ordre.selection_nbest(population, n_selected, scores, verbose=True)
        else:
            best_ordres = ordre.selection_nbest(population, n_selected, scores)
        if graph_evolution:
            graph_evo_best.append(best_ordres[0])
        # mutations
        mutated_ordres = []
        for i in range(n_mutated):
            add_index = np.random.randint(0, n_selected, 1)[0]
            mutated_ordres.append(best_ordres[add_index].mutation_multiple_out(nb_mut_max, mutation_prob, tasks_dict))
        # crossovers
        cross_ordres = []
        for i in range(n_crossed):
            parents = np.random.randint(0, n_selected, 2)
            bloc_size = np.random.randint(crossover_bloc_size[0], crossover_bloc_size[1])
            cross_ordres.append(ordre.crossover_2_parents(best_ordres[parents[0]], best_ordres[parents[1]], bloc_size))
        # evaluations
        population = best_ordres + mutated_ordres + cross_ordres
        scores = ordre.population_eval(population, n_cores, tasks_dict, optimal_time)
        # legality checking
        if verify_legality:
            for ind in population:
                if not ind.isLegal(tasks_dict, n_tasks):
                    return f'ERROR !!! illegal order thrown at ' + str(ind)
        # time_analytics
        if time_analytics:
            ana_ordres.append(best_ordres[0].ordre)
            ana_scores.append(scores[0])
            ana_means.append(ordre.mean(scores))

    # log results to the console
    bar = '\n_________________________________________________________________'
    print('\n' + bar + '\n_______________________________RESULTS_______________________________' + bar + '\n')
    best_result = ordre.selection_nbest(population, 1, scores)[0]
    print(best_result)
    print('the best ordre has a score of : ', ordre.population_eval([best_result], n_cores, tasks_dict, optimal_time)[0])
    print(bar + '\n\n')

    # time_analytics score printing
    if time_analytics:
        analysis.performance_evaluation(ana_scores, ana_means)

    # graph printing
    if colored_graph_displaying:
        printgraph.print_color_graph(tasks_dict, best_result)

    # graph evolution
    if graph_evolution:
        pos = printgraph.getpos(tasks_dict)
        for i in range(epochs):
            printgraph.print_color_graph(tasks_dict, graph_evo_best[i], pos=pos, title=f'best at epoch {i}')
    return best_result


if __name__ == "__main__" :
    # START ALGO
    start_time = time()
    best_result = main_genetics(path_graph, n_population, n_cores, n_selected, n_mutated, n_crossed, mutations_prob, nb_mut_max, crossover_bloc_size, epochs, verbose=verbose, time_analytics=time_analytics, colored_graph_displaying=colored_graph_displaying, verify_legality=verify_legality, graph_evolution=graph_evolution)
    end_time = time()
    print('Total Time : {0} s'.format(end_time-start_time))