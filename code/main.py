import numpy as np
import initialisation
import task
import ordre
import data_loading as dtld
import time_personalized
from pathlib import Path

# graph to use
data_folder = Path("../graphs")
path_graph = data_folder / "smallRandom.json"
print(path_graph)
# parameters
n_population = 10


def test_ordre(path_graph, n_population, mutate_test=False):
    # Load the tasks
    tasks_dict = dtld.loadTasks(path_graph)
    optimal_time = dtld.ideal_time(tasks_dict)

    # creation d'ordres
    ordre_arbitrary1 = [1, 2, 3, 4, 5, 6, 7, 10, 8, 9]
    ordre1 = np.array([tasks_dict[i] for i in ordre_arbitrary1])
    ordre_arbitrary2 = [1, 3, 6, 2, 4, 5, 7, 8, 9, 10]
    ordre2 = np.array([tasks_dict[i] for i in ordre_arbitrary2])

    test_ordre1 = ordre.Ordre(ordre1)
    test_ordre2 = ordre.Ordre(ordre2)
    test_ordre_empty = ordre.Ordre(np.array([]))
    test_ordre_error = ordre.Ordre([None])  # throws an error, then this ordre becomes an empty one

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

    print(CpuOrder12)
    print(CpuOrder14)

    ratio_1_4 = time_personalized.metric_ratio(time_taken_1_4, optimal_time)*4
    print(ratio_1_4)
    ratio_2_4 = time_personalized.metric_ratio(time_taken_1_4, optimal_time)*4
    print(ratio_2_4)
    ratio_1_2 = time_personalized.metric_ratio(time_taken_1_4, optimal_time)*2
    print(ratio_1_2)

    # TODO : always the same time scheduled figure out


mutate_test = False
test_ordre(path_graph, n_population, mutate_test)








'''



def main():
    population = []
    n = 10
    # ___________ N = 4
    # Création d'une mini population de 10individus
    for k in range(n):
        tasks = data_loading.loadTasks('mediumRandom.json')
        population.append(ordre.Ordre(tasks))
    for k in range(n):
        for mut in range(1000): # chaque individu subit 20 mutation pour se différencier
            population[k].mutation()
    population = ordre.selection(population,n)
    for k in range(len(population)):
        print(population[k].CPUScheduling())
    

    for k in range(5): # On fait 5 itérations
        ordre.croisement_pop(population,10) # On croise par block de 10
        ordre.mutation_pop(population,0.5,1000) # Puis on mute 50%


        # On ne garde que les 10meilleurs
        population = ordre.selection(population,n)

    print("////:")
    for k in range(len(population)):
        print(population[k].CPUScheduling())

    pass
'''