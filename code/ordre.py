import numpy as np
from math import ceil
import json
import time_personalized
import node



# number of cores to use
N = 4

class ordre:
    def __init__(self, ordre):
        self.ordre = ordre

    def dependances(self, CpuOrder, tache):
        listDep = tache.dependance
        maxTime = time_personalized.time(0, 0, 0, 0)
        for i in range(0, N):
            if CpuOrder[i] == []:
                timeAc = time_personalized.time(0, 0, 0, 0)
            else:
                node = CpuOrder[i][-1]
                if int(node[0].ID) in listDep:
                    timeAc = node[0].time
                else:
                    timeAc = time_personalized.time(0, 0, 0, 0)
            if maxTime.isSmaller(timeAc):
                maxTime = timeAc
        return maxTime

    def ordreToCPU(self):
        CpuOrder = [[] for _ in range(0, N)]
        times = [time_personalized.time(0, 0, 0, 0) for _ in range(0, N)]
        for tache in self.ordre:
            k = time_personalized.argmini(times)
            beginTime = times[k].add(self.dependances(CpuOrder, tache)) 
            CpuOrder[k].append([tache, beginTime])
            times[k] = beginTime.add(tache.time)
        return time_personalized.maxTime(times)

    def mutation(self):
        ind_inf = 0
        n = len(self.ordre)
        ind_sup = n-1
        ind_mut = np.random.randint(0, n)
        node_mut = self.ordre[ind_mut]
        for k in range(ind_mut):
            node = self.ordre[k]
            if int(node.ID) in node_mut.dependance:
                ind_inf = k + 1
        for k in range(n - ind_mut -1):
            node = self.ordre[n - k - 1]
            if int(node_mut.ID) in node.dependance:
                ind_sup = n - k - 2
        ind_new = np.random.randint(ind_inf, ind_sup + 1)
        del self.ordre[ind_mut]
        self.ordre.insert(ind_new, node_mut)


def croisement(ordre1, ordre2, bloc_taille=1):
    '''
    Utiliser par exemple : nouvelordre = croisement(ordre1, ordre2)
    Attention : ordre1 et 2 doivent etre un objet, mais pas une liste
    Notez : Il faut assurer ordre1 et ordre2 ont la meme taille
    '''
    assert len(ordre1.ordre) == len(ordre2.ordre)
    ordre_nouvel = []
    ID_list = []

    for i in range(ceil(len(ordre1.ordre) / bloc_taille)):
        temp_list = ordre1.ordre[i * bloc_taille: (i + 1) * bloc_taille] + ordre2.ordre[
            i * bloc_taille: (i + 1) * bloc_taille]
        for node_in_list in temp_list:
            if node_in_list.ID not in ID_list:
                ordre_nouvel.append(node_in_list)
                ID_list.append(node_in_list.ID)
    return ordre(ordre_nouvel)

def mutation_pop(population,prob_mutation, nb_mutation):
    for k in range(len(population)):
        if np.random.random() < prob_mutation:
            new_ordre = list(population[k].ordre)
            population.append(ordre( new_ordre ))
            for k in range(nb_mutation):
                population[-1].mutation()

def croisement_pop(population, size_block):
    for k in range(len(population)//2):
        ordre1 = population[2*k]
        ordre2 = population[2*k+1]
        population.append(croisement(ordre1,ordre2,size_block))
    
def print_ordre(ordre):
    for k in range(len(ordre.ordre)):
        print(ordre.ordre[k].ID)

def selection(population, n):
    # On conserve n individu de la population initial
    classement = []
    pop_final =  []
    for k in range(len(population)):
        time = population[k].ordreToCPU()
        if len(classement)<n:
            if(len(classement)==0):
                classement.append([ population[k],time ])
            else:
                for j in range(len(classement)):
                    if classement[j][1].isSmaller(time):
                        classement.insert(j,[ population[k],time ])
                        break
                    elif(j==len(classement)-1):
                        classement.append([ population[k],time ])
        else:
            for j in range(n):
                if classement[j][1].isSmaller(time):
                    if j==0:
                        break
                    else:
                        del classement[0]
                        classement.insert(j-1,[ population[k],time ])
                        break
    for k in range(len(classement)):
        pop_final.append( classement[k][0] )
    return pop_final