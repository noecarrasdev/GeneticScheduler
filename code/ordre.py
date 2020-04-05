import numpy as np
from math import ceil
import time_personalized
import task
from copy import deepcopy
#import mpi4py
#from mpi4py import MPI

# CODE
'''
Comm = MPI.COMM_WORLD
size = Comm.Get_size() 
rank = Comm.Get_rank()
'''
class Ordre:
    def __init__(self, ordre):
        '''
        :param ordre: np.array([task])
        there's no test of this in this function but be careful with it !
        '''
        try:
            if type(ordre) == type(np.array([1])):
                self.ordre = ordre
            else:
                print('give an array')
        except:
            print('unexpected error')
            self.ordre = np.array([])

    def __gt__(self, other): 
        if(self.ordre>other.ordre): 
            return True
        else: 
            return False

    def __lt__(self, other): 
        return True
    def __eq__(self, other): 
        if(np.all(np.equal(self.ordre,other.ordre))): 
            return True
        else: 
            return False

    def __str__(self):
        n = len(self.ordre)
        message = 'Ordre : '
        if n > 0:
            for k in range(n):
                message += (str(self.ordre[k]) + ' - ')
        elif n == 0:
            message = 'empty Ordre'
        else:
            message = 'error'
        return message

    def newTime(self, cpuord, tasks_dict, times, task, minCore, n_cores):
        '''
        :params: from CPUScheduling
        :return: the TimeTask object of when to start the new task
        '''
        max_time = times[minCore]
        if n_cores == 0:
            return 'error : no cores to compute on'
        if n_cores == 1:
            return max_time
        for i_core in range(n_cores):
            if i_core != minCore:
                if times[minCore].isSmaller(times[i_core]):
                    currentID = cpuord[i_core][-1][0]
                    if currentID in tasks_dict[task].dependence:
                        new_time = cpuord[i_core][-1][1].add(cpuord[i_core][-1][2])
                        if max_time.isSmaller(new_time):
                            max_time = new_time
        return max_time

    def CPUScheduling(self, n_cores, tasks_dict, verbose=False):
        '''
        gives the order of the tasks in the CPU and the time taken to compute everything
        :return: 2 things :
        - total computational time (:type: TaskTime)
        - scheduling of the tasks (:type: [N * [[task, beginTime], [task, beginTime], ...] ])
        '''
        CpuOrder = [[] for _ in range(0, n_cores)]
        times = [time_personalized.TimeTask(0, 0, 0, 0) for _ in range(0, n_cores)]

        for task in self.ordre:
            if verbose:
                print(f'for the task {task}, the times are : ')
                for i in range(len(times)):
                    print(f'core {i} is at time : ', times[i])

            # finding the core with the smallest time
            minCore = time_personalized.argmini(times)

            # find until when to wait on this core (resolve the Dependancies)
            beginTime = self.newTime(CpuOrder, tasks_dict, times, task, minCore, n_cores)

            # updates the informations to continue with next tasks
            lengthTime = tasks_dict[task].time
            CpuOrder[minCore].append([task, lengthTime, beginTime])
            if verbose:
                print('for this task, the time taken is : ', lengthTime)
            times[minCore] = beginTime.add(lengthTime)

            if verbose:
                print(f'after the execution on this task, we are at : ')
                for i in range(len(times)):
                    print(f'core {i} is at time : ', times[i])
                print('\n')

        return time_personalized.maxTime(times), CpuOrder

    def mutation_multiple_out(self, n_mutation, prob_mut, tasks_dict, verbose=False):
        '''
        returns a mutated individual, works on a simple list with task_dependencies to be easier for the memory
        :param n_mutation: int, maximum number of mutations
        :param prob_mut: float, probability than each mutation occurs
        :param tasks_dict: dict, indexed by int
        :return:
        '''
        # creating a list that's the image of self.ordre
        new_seed = []
        n = len(self.ordre)
        for i in range(n):
            new_seed.append(deepcopy(self.ordre[i]))
        # mutate that list
        if verbose:
            print('\nFirst seed', new_seed)
        for i in range(n_mutation):
            if np.random.uniform() < prob_mut:
                # The task to move
                ind_mut = np.random.randint(0, n)
                task_mut = new_seed[ind_mut]
                task_dep = tasks_dict[task_mut].dependence
                # finding borders
                ind_inf = deepcopy(ind_mut)
                ind_sup = deepcopy(ind_mut)
                while ind_inf > 0 and (tasks_dict[new_seed[ind_inf]].ID not in task_dep):
                    ind_inf -= 1
                if ind_inf > 0 or (tasks_dict[new_seed[ind_inf]].ID in task_dep):
                    ind_inf += 1
                while ind_sup < n and (task_mut not in tasks_dict[new_seed[ind_sup]].dependence):
                    ind_sup += 1
                if not (ind_sup < n and (task_mut not in tasks_dict[new_seed[ind_sup]].dependence)):
                    ind_sup -= 1
                if verbose:
                    print(f'ind_mut is {ind_mut}, task is {task_mut}, ind_inf is {ind_inf}, ind_sup is {ind_sup}')
                # finding inserting index
                ind_insert = np.random.randint(ind_inf, ind_sup + 1)
                above = (ind_insert >= ind_mut)
                # inserting in the list
                new_seed.insert(ind_insert, task_mut)
                if above:
                    new_seed.pop(ind_mut)
                else:
                    new_seed.pop(ind_mut + 1)
                if verbose:
                    print('after a mutation', new_seed)

        return Ordre(np.array(new_seed))

    def isLegal(self, tasks_dict, number_of_tasks):
        '''
        :param number_of_tasks: number of tasks in the whole graph
        :return: Boolean representing if this ordre is valid
        '''
        if len(self.ordre) != number_of_tasks:
            print('wrong number of tasks')
            return False
        resolved_tasks = []
        for task in self.ordre:
            for dependency in tasks_dict[task].dependence:
                if dependency not in resolved_tasks:
                    print(f'{task.ID} is wrong because it appears before its dependency {dependency}')
                    return False
            resolved_tasks.append(task)
        return True


def crossover_2_parents(parent_ordre1, parent_ordre2, bloc_taille=2):
    # TODO : améliorer ça pour mettre plus de parents possibles
    # TODO : utilité de blocs de taille variable ?
    '''
    :param ordre1: Ordre
    :param ordre2: Ordre
    :param bloc_taille: size of the chunks to keep
    :return: Ordre issued from the crossover
    '''
    new_ordre = []
    ordre1 = parent_ordre1.ordre
    ordre2 = parent_ordre2.ordre
    assert len(ordre1) == len(ordre2)

    for i in range(ceil(len(ordre1) / bloc_taille)):
        temp_list1 = ordre1[i * bloc_taille: (i + 1) * bloc_taille]
        temp_list2 = ordre2[i * bloc_taille: (i + 1) * bloc_taille]
        for tpl in (temp_list1, temp_list2):
            for task in tpl:
                if task not in new_ordre:
                    new_ordre.append(task)
    return Ordre(np.array(new_ordre))


def print_ordre(ordre):
    '''
    :param ordre:
    :return: void
    print the ID order
    '''
    for k in range(len(ordre.ordre)):
        print(ordre.ordre[k])


def print_cpuord(cpuord):
    '''
    :param cpuord: list of the form [N * [task (Task object), beginigTime (TimeTask object)]]
    :return: np.array() of proper strings describing the cpu order
    '''
    end_list = [[f'core {i}'] for i in range(len(cpuord))]
    for i_cpu in range(len(cpuord)):
        for i_task in range(len(cpuord[i_cpu])):
            taskandtime = cpuord[i_cpu][i_task]
            # print(i_cpu, i_task, taskandtime)
            try:
                if (taskandtime and len(taskandtime) == 2):
                    end_list[i_cpu].append((str(taskandtime[0]), str(taskandtime[1])))
                else:
                    print(f'error, empty entry at {i_cpu} core and over {i_task} entry')
            except:
                print(f'real error happened !! at {i_cpu} core and over {i_task} entry')
    return end_list


def selection_nbest_eval_inside(population, n, verbose=True):
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


def selection_nbest(population, n, scores, verbose=False):
    '''
    :param population: [Ordre] to update
    :param n: number of orders to keep
    :param scores: list of the scores of the population (score = tps/(optimal/nbCPU))
    :param verbose: Boolean to log into the console
    :return: the new population
    '''

    n_pop = len(population)

    if n > n_pop:
        return 'error : you tried to select more nodes that there is in the population'

    if verbose:
        best_scores = [None] * n

    # indexes of the biggest indexes in decreasing order
    score_ranks = sorted(range(len(scores)), key=lambda i: scores[i])
    best_elements = [None] * n
    for i in range(n):
        best_elements[i] = population[score_ranks[i]]
        if verbose:
            best_scores[i] = scores[score_ranks[i]]

    if verbose:
        print('best    : ', best_scores[0])
        print('average : ', mean(best_scores))

    return best_elements


def mean(L):
    '''
    :param L: list
    :return: mean value
    '''
    sum = 0
    for x in L:
        sum += x
    n = len(L)
    if n > 0:
        result = sum / len(L)
    else:
        result = 0
    return result


def population_eval(pop, n_cores, tasks_dict, optimal):
    '''
    :param pop: list of Ordres
    :return: list of scores (corresponding to the ordres with the same indexes)
    '''
    scores = []
    for ind in pop:
        scores.append(-1 + n_cores * time_personalized.metric_ratio(ind.CPUScheduling(n_cores, tasks_dict)[0], optimal))
    return scores

# TESTS in the main file
