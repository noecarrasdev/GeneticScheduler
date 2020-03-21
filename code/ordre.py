import numpy as np
from math import ceil
import time_personalized
import task


# CODE

class Ordre:
    def __init__(self, ordre):
        '''
        :param ordre: np.array([task])
        there's no test of this in this function but be careful with it !
        '''
        try:
            if type(ordre) == type(np.array([1])):
                if len(ordre) == 0 or type(ordre[0]) == type(task.Task(1, time_personalized.TimeTask(1, 2, 3, 4), [])):
                    self.ordre = ordre
                else:
                    print('must be Task inside of the array')
                    self.ordre = np.array([])
            else:
                print('must be a np.array')
                self.ordre = np.array([])
        except:
            print('unexpected error')
            self.ordre = np.array([])

    def __str__(self):
        n = len(self.ordre)
        message = 'Ordre : '
        if n > 0:
            for k in range(n):
                message += (str(self.ordre[k].ID) + ' - ')
        elif n == 0:
            message = 'empty Ordre'
        else:
            message = 'error'
        return message

    def waitingTime(self, CpuOrder, task, N):
        '''
        :param CpuOrder: an order of tasks in the CPU
        :param task: next Task to add
        :param N: number of cores
        :return: TaskTime of the time needed to wait to place the new task
        '''
        listDep = task.dependence
        maxTime = time_personalized.TimeTask(0, 0, 0, 0)
        for i in range(0, N):
            # first task of a core
            if not CpuOrder[i]:
                timeAc = time_personalized.TimeTask(0, 0, 0, 0)
            else:
                other_task = CpuOrder[i][-1]
                # the other task is a dependency
                if other_task[0].ID in listDep:
                    timeAc = other_task[0].time
                # it isn't
                else:
                    timeAc = time_personalized.TimeTask(0, 0, 0, 0)
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
        times = [time_personalized.TimeTask(0, 0, 0, 0) for _ in range(0, N)]

        for task in self.ordre:
            # finding the core with the smallest time
            minCore = time_personalized.argmini(times)

            # find until when to wait on this core (resolve the Dependancies)
            beginTime = times[minCore].add(self.waitingTime(CpuOrder, task, N))

            # updates the informations to continue with next tasks
            CpuOrder[minCore].append([task, beginTime])
            times[minCore] = beginTime.add(task.time)

        return time_personalized.maxTime(times), CpuOrder


    def mutation_in_place(self):
        '''
        randomly mutates on 1 task in this Ordre
        :return: void
        '''
        ind_inf = 0
        n = len(self.ordre)
        ind_sup = n-1
        ind_mut = np.random.randint(0, n)
        task_mut = self.ordre[ind_mut]
        for k in range(ind_mut):
            task = self.ordre[k]
            if int(task.ID) in task_mut.dependence:
                ind_inf = k + 1
        for k in range(n - ind_mut - 1):
            task = self.ordre[n - k - 1]
            if int(task_mut.ID) in task.dependence:
                ind_sup = n - k - 2
        ind_new = ind_mut
        while ind_new == ind_mut:
            ind_new = np.random.randint(ind_inf, ind_sup + 1)
        outordre = np.insert(np.delete(self.ordre, ind_mut), ind_new, task_mut)
        self.ordre = outordre

    def mutation_out(self):
        '''
        randomly mutates on 1 task in this Ordre
        :return: void
        '''
        ind_inf = 0
        n = len(self.ordre)
        ind_sup = n-1
        ind_mut = np.random.randint(0, n)
        task_mut = self.ordre[ind_mut]
        for k in range(ind_mut):
            task = self.ordre[k]
            if int(task.ID) in task_mut.dependence:
                ind_inf = k + 1
        for k in range(n - ind_mut -1):
            task = self.ordre[n - k - 1]
            if int(task_mut.ID) in task.dependence:
                ind_sup = n - k - 2
        ind_new = ind_mut
        while ind_new == ind_mut:
            ind_new = np.random.randint(ind_inf, ind_sup + 1)
        outordre = Ordre(np.insert(np.delete(self.ordre, ind_mut), ind_new, task_mut))
        return outordre

    def isLegal(self, number_of_tasks):
        '''
        :param number_of_tasks: number of tasks in the whole graph
        :return: Boolean representing if this ordre is valid
        '''
        if len(self.ordre) != number_of_tasks:
            return False
        resolved_tasks = []
        for task in self.ordre:
            for dependency in task.dependence:
                if dependency not in resolved_tasks:
                    return False
            resolved_tasks.append(task.ID)
        return True


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
                population[k].mutation_in_place()


def crossover_2_parents(parent_ordre1, parent_ordre2, bloc_taille=2):
    # TODO : améliorer ça pour mettre plus de parents possibles
    # TODO : utilité de blocs de taille variable ?
    '''
    :param ordre1: Ordre
    :param ordre2: Ordre
    :param bloc_taille: size of the chunks to keep
    :return: Ordre issued from the crossover
    '''
    ordre_nouvel = []
    ID_list = []
    ordre1 = parent_ordre1.ordre
    ordre2 = parent_ordre2.ordre
    assert len(ordre1) == len(ordre2)

    for i in range(ceil(len(ordre1) / bloc_taille)):
        temp_list1 = ordre1[i * bloc_taille: (i + 1) * bloc_taille]
        temp_list2 = ordre2[i * bloc_taille: (i + 1) * bloc_taille]
        for tpl in (temp_list1, temp_list2):
            for task in tpl:
                if task.ID not in ID_list:
                    ordre_nouvel.append(task)
                    ID_list.append(task.ID)
    return Ordre(np.array(ordre_nouvel))


def croisement_pop(population, size_block):
    # TODO : améliorer ça...
    for k in range(len(population)//2):
        ordre1 = population[2*k]
        ordre2 = population[2*k+1]
        population.append(crossover_2_parents(ordre1, ordre2, size_block))


def print_ordre(ordre):
    '''
    :param ordre:
    :return: void
    print the ID order
    '''
    for k in range(len(ordre.ordre)):
        print(ordre.ordre[k].ID)


def print_cpuord(cpuord):
    '''
    :param cpuord: list of the form [N * [task (Task object), beginigTime (TimeTask object)]]
    :return: np.array() of proper strings describing the cpu order
    '''
    end_list = [[f'core {i}'] for i in range(len(cpuord))]
    for i_cpu in range(len(cpuord)):
        for i_task in range(len(cpuord[i_cpu])):
            taskandtime = cpuord[i_cpu][i_task]
            #print(i_cpu, i_task, taskandtime)
            try:
                if (taskandtime and len(taskandtime) == 2):
                    end_list[i_cpu].append((str(taskandtime[0]), str(taskandtime[1])))
                else:
                    print(f'error, empty entry at {i_cpu} core and over {i_task} entry')
            except:
                print(f'real error happened !! at {i_cpu} core and over {i_task} entry')
    return end_list

def selection_nbest(population, n, verbose=True):
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


# TESTS in the main file (requires more than this file only)
