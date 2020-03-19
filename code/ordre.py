import numpy as np
from math import ceil
import time_personalized
import task

# TEST LAUNCH

testLaunch = True


# CODE

class Ordre:
    def __init__(self, ordre):
        '''
        :param ordre: np.array([integers])
        there's no test of this in this function but be careful with it !
        '''
        self.ordre = ordre

    def waitingTime(self, CpuOrder, task):
        '''
        :param CpuOrder: an order of tasks in the CPU
        :param task: next Task to add
        :return: TaskTime of the time needed to wait to place the new task
        '''
        listDep = task.dependance
        maxTime = time_personalized.TaskTime(0, 0, 0, 0)
        for i in range(0, N):
            # first task of a core
            if CpuOrder[i] == []:
                timeAc = time_personalized.TaskTime(0, 0, 0, 0)
            else:
                other_task = CpuOrder[i][-1]
                # the other task is a dependency
                if other_task[0].ID in listDep:
                    timeAc = other_task[0].time
                # it isn't
                else:
                    timeAc = time_personalized.TaskTime(0, 0, 0, 0)
            if maxTime.isSmaller(timeAc):
                maxTime = timeAc
        return maxTime

    def CPUScheduling(self, N):
        '''
        gives the order of the tasks in the CPU and the time taken to compute everything
        :return: 2 things :
        - total computational time (:type: TaskTime)
        - scheduling of the tasks (:type: [N * [[task, beginTime], [task, beginTime], ...] ])
        '''
        CpuOrder = [[] for _ in range(0, N)]
        times = [time_personalized.time(0, 0, 0, 0) for _ in range(0, N)]

        for task in self.ordre:
            # finding the core with the smallest time
            minCore = time_personalized.argmini(times)

            # find until when to wait on this core (resolve the Dependancies)
            beginTime = times[minCore].add(self.waitingTime(CpuOrder, task))

            # updates the informations to continue with next tasks
            CpuOrder[minCore].append([task, beginTime])
            times[minCore] = beginTime.add(task.time)

        return time_personalized.maxTime(times), CpuOrder


    def mutation(self):
        '''
        randomly mutates on 1 task in this Ordre
        :return:
        '''
        ind_inf = 0
        n = len(self.ordre)
        ind_sup = n-1
        ind_mut = np.random.randint(0, n)
        task_mut = self.ordre[ind_mut]
        for k in range(ind_mut):
            task = self.ordre[k]
            if int(task.ID) in task_mut.dependance:
                ind_inf = k + 1
        for k in range(n - ind_mut -1):
            task = self.ordre[n - k - 1]
            if int(task_mut.ID) in task.dependance:
                ind_sup = n - k - 2
        ind_new = np.random.randint(ind_inf, ind_sup + 1)
        del self.ordre[ind_mut]
        self.ordre.insert(ind_new, task_mut)


def mutation_pop(population, prob_mutation, nb_max_mutation):
    '''
    :param population: list of Ordre
    :param prob_mutation: probability that each time an individual mutates
    :param nb_max_mutation: maximum number of mutation that 1 individual can make
    :return: void
    updates to population in place to save space & time
    '''
    for k in range(len(population)):
        for i in range(nb_max_mutation):
            if np.random.random() < prob_mutation:
                population[k].mutation()


def croisement(ordre1, ordre2, bloc_taille=1):
    # TODO : améliorer ça pour mettre plus de parents possibles
    # TODO : utilité de blocs de taille variable ?
    '''
    :param ordre1: Ordre
    :param ordre2: Ordre
    :param bloc_taille: size of the chunks to keep
    :return: Ordre issued from the crossover
    '''
    assert len(ordre1.ordre) == len(ordre2.ordre)
    ordre_nouvel = []
    ID_list = []

    for i in range(ceil(len(ordre1.ordre) / bloc_taille)):
        temp_list = ordre1.ordre[i * bloc_taille: (i + 1) * bloc_taille] + ordre2.ordre[
            i * bloc_taille: (i + 1) * bloc_taille]
        for task in temp_list:
            if task.ID not in ID_list:
                ordre_nouvel.append(task)
                ID_list.append(task.ID)
    return Ordre(ordre_nouvel)


def croisement_pop(population, size_block):
    # TODO : améliorer ça...
    for k in range(len(population)//2):
        ordre1 = population[2*k]
        ordre2 = population[2*k+1]
        population.append(croisement(ordre1,ordre2,size_block))


def print_ordre(ordre):
    '''
    :param ordre:
    :return: void
    print the ID order
    '''
    for k in range(len(ordre.ordre)):
        print(ordre.ordre[k].ID)


def selection(population, n, verbose):
    '''
    :param population: [Ordre] to update
    :param n: number of orders to keep
    :param verbose: Boolean to log into the console
    :return: the new population
    '''

    if n > len(population):
        return 'error : you tried to select more nodes that there is in the population'

    evaluation = {}
    pop_final = []

    for k in range(len(population)):
        evaluation[k] = population[k].CPUScheduling[0]

    for key, value in sorted(evaluation.items(), key=lambda x: x[1])[:n]:
        if verbose:
            print(f'{key} is selected with a score of {value}. The combination is {print_ordre(population[key])}')
        pop_final.append(population[key])

    return pop_final


# TESTS

if testLaunch:
    # TODO : implement small tests to test all the functions
    pass
