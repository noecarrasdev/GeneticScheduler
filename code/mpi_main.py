# Import MPI
from mpi4py import MPI
# Import other packages
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
from ordre import Ordre



def selection_nbest_mpi(population, n, scores, verbose=False):
    '''
    :param population: [Ordre] to update
    :param n: number of orders to keep
    :param scores: list of the scores of the population (score = tps/(optimal/nbCPU))
    :param verbose: Boolean to log into the console
    :return: the new population

    Note that n%NbP has to be 0, and n//NbP must > 1
    '''
    global comm, NbP, Me , dict_ordres
    d=int(np.log2(NbP)) #dimension du cube
    tab_inf = None                         #ce qu'on va utiliser pour transmettre les données
    tab_sup = None
    pivot = None
    dtype=[("individu", int),("score",float)]  #type qu'on va utiliser pour trier avec np.sort
    data = []

    n_pop = len(population)

    if n > n_pop * NbP:
        return 'error : you tried to select more nodes that there is in the population'
     

    def remplir_dict_ordre(tab) :  #on rempli le dico et en fait une list d'ID
        # entrée tableau des ordre
        # sortie liste des IDs qui associe un nombre à un ordre
        res=[]
        for k in tab :
            res.append(len(dict_ordres))
            dict_ordres.append(k)
        return(res)
    

    def binary2int(tab) :
        #donne l'entier de la representation binaire
        res = 0
        for i in range(len(tab)) :
            res+=(2**i)*tab[i]
        return(res)

    def int2binary(n) :
        #donne le representation binaire dans un table depuis un entier 
        bin = np.binary_repr(int(n))
        res = np.zeros(d)
        for i in range(len(bin)) :
            res[i] = (bin[-(i+1)])    
        return(res)

    def separation_pop_score(tab) :
        """pour séparer lpop et score pour l'envoie en MPI"""
        n=len(tab)
        if n==0 :
            return (np.empty(0),np.empty(0))
        else :
            res1=[]
            res2 = []
            for i in range(n) :
                res1.append(tab[i][0])              
                res2.append(tab[i][1])
            return(np.array(res1),np.array(res2))

    def reunion_pop_score(tab_pop,tab_score) :
        """pour réunir pop et score en une table"""
        n = len(tab_pop)
        if n == 0 : 
            return([])
        else :
            res=[]
            for i in range(n) :
               res.append((tab_pop[i],tab_score[i]))
            return(res)
    
    def tab2ordre(tab) :
        #entrée : list des Ids
        #sortie : list des ordres coresspondants aux Ids
        res=[]
        for i in tab :
            res.append(dict_ordres[int(i)])
        return res 



    
    def partition(tab,x) :
        """separer la liste en 2 liste une dont les individus avec un score <=x et lautres >x"""
        tab_i=[]
        tab_s=[]
        for k in tab :
            if k[1]<=x :
                tab_i.append(k)
            else :
                tab_s.append(k)
        return(np.array(tab_i,dtype=dtype),np.array(tab_s,dtype=dtype))
    

    """on effectue le tri rapide sur hypercube en simultané sur tous les coeurs"""
    for i in range(NbP) :
        if Me == i :                    #pour chaque coeur on rempli le dictionnaire et on recupere la table des identifiants des ordres
            population = remplir_dict_ordre(population)
    for i in range(len(population)) :    #creation de liste regroupant la population et score
        data.append((population[i],scores[i]))         
    data = np.array(data,dtype=dtype)    #on type l'array pour le trier
    
    
    data = np.sort(data, order="score")    # on trie sur les scores, tri initial 
    for i in range(d-1,-1,-1) :
        if np.all(np.equal(int2binary(Me)[:i+1],np.zeros(i+1))) : #choix des coeurs qui donneront un pivot
            m=len(data)
            if len(data) != 0:
                pivot = data[m//2][1]  #on prend la mediane en pivot
            else :
                pivot = 0                       
            for j in range(2**(i+1)-1) :                   #on envoie le pivot aux coeurs qui ne calculerons pas de pivot
                comm.send(pivot,Me+j+1)
        else : 
            target = np.copy(int2binary(Me))        #sinon on prend le pivot du coeurs associé
            for j in range(i+1) :
                target[j] = 0
            target = binary2int(target)
            pivot = comm.recv(source=target)

        tab_inf,tab_sup = partition(data,pivot)        #on partitionne en fonction du pivot
        if int2binary(Me)[i] ==0 :
            target = np.copy(int2binary(Me))
            target[i]=1
            target = binary2int(target)
            numData=len(tab_sup)                    #on envoie et recupere le nombre de donnees a envoyer ou recvoir
            comm.send(numData,dest=target)
            numData_rec = comm.recv(source=target)
            tab_buf_pop = np.empty(numData_rec)
            tab_buf_scores = np.empty(numData_rec)

        else :
            target = np.copy(int2binary(Me))
            target[i] = 0
            target = binary2int(target)
            numData=len(tab_inf)
            comm.send(numData,dest=target)
            numData_rec= comm.recv(source=target)
            tab_buf_pop = np.empty(numData_rec)
            tab_buf_scores = np.empty(numData_rec)
        
        if int2binary(Me)[i] ==0 :
            tab_sup_pop,tab_sup_score = separation_pop_score(tab_sup)                  #on envoie/recoit les donnees de population et score
            comm.Send(tab_sup_pop,dest=target)
            comm.Send(tab_sup_score,dest = target)
            comm.Recv(tab_buf_pop,source=target)
            comm.Recv(tab_buf_scores,source=target)
            tab_buf = reunion_pop_score(tab_buf_pop,tab_buf_scores)              #on rassemble les table population et score 
            tab_buf = np.array(tab_buf,dtype=dtype)
            data = np.sort(np.concatenate((tab_inf,tab_buf)),order = "score")    #on fait l'union des deux liste en ordonnant
        else :
            tab_inf_pop,tab_inf_score = separation_pop_score(tab_inf)                  #on envoie/recoit les donnees
            comm.Send(tab_inf_pop,dest=target)
            comm.Send(tab_inf_score,dest=target)
            comm.Recv(tab_buf_pop,source=target)
            comm.Recv(tab_buf_scores,source=target)        
            tab_buf = reunion_pop_score(tab_buf_pop,tab_buf_scores)
            tab_buf = np.array(tab_buf,dtype=dtype)
            data = np.sort(np.concatenate((tab_sup,tab_buf)),order = "score")    #on fait l'union des deux liste en ordonnant
    if Me == 0 :
        best_elements = np.array([k[0]for k in data])   #on recupere uniquement les individus en array sans les scores
        if len(best_elements)>n :     #on prend que les n meilleurs si jamais on en a trop 
            best_elements = best_elements[:n]
        numDatasend_bcast = len(best_elements)
    else :
        numDatasend_bcast = None
    numDatasend_bcast = comm.bcast(numDatasend_bcast,root=0)        #on broadcast le nombre de donnees qu'on va envoyer

    if Me != 0 : 
        best_elements = np.empty(numDatasend_bcast)
    comm.Bcast(best_elements,root=0)                      # on broadcast les meilleurs elements qui sont sur le coeur 0
    best_elements = tab2ordre(best_elements) #on repasse avec des ordre
    
    dict_ordres = []                  # on vide le dictionnaire des ordre
    return (best_elements)


def main_genetics(path_graph, n_population, n_cores, n_selected, n_mutated, n_crossed,
                  mutation_prob, nb_mut_max, crossover_bloc_size, epochs, verbose=True,
                  time_analytics=True, colored_graph_displaying=True, blank_analysis=True,
                  verify_legality=False, graph_evolution=False):
    '''
    Main call function that starts the genetic algorithm
    '''

    # MPI stuff as global variables
    global NbP, Me

    # load datas
    tasks_dict = dtld.loadTasks(path_graph)
    n_tasks = len(tasks_dict.keys())
    optimal_time = dtld.ideal_time(tasks_dict)

    # initial population
    population = initialisation.population_initiale(tasks_dict, n_population //NbP)
    scores = ordre.population_eval(population, n_cores, tasks_dict, optimal_time)

    # time_analytics
    ana_ordres = []
    ana_scores = []
    ana_means = []

    # graph evolution
    graph_evo_best = []

    keep_best_result_azure = []

    # execution
    for epoch in range(epochs):
        if verbose and Me == 0:
            print(f'\n__________epoch n{epoch}_________')
            BEST = selection_nbest_mpi(population, n_selected, scores)[0]
            keep_best_result_azure.append(ordre.population_eval([BEST], n_cores, tasks_dict, optimal_time)[0])
            print('the best ordre epochs has a score of : ', ordre.population_eval([BEST], n_cores, tasks_dict, optimal_time)[0])
        # selection of the bests
        best_ordres = selection_nbest_mpi(population, n_selected, scores, verbose=verbose)

        if graph_evolution and Me == 0:
            graph_evo_best.append(best_ordres[0])
        # mutations
        mutated_ordres = []
        for _ in range(n_mutated // NbP):
            add_index = np.random.randint(0, n_selected // NbP +1 , 1)[0]
            mutated_ordres.append(best_ordres[add_index].mutation_multiple_out(nb_mut_max, mutation_prob, tasks_dict))
        # crossovers
        cross_ordres = []
        for _ in range(n_crossed // NbP):
            parents = np.random.randint(0, n_selected // NbP +1, 2)
            bloc_size = np.random.randint(crossover_bloc_size[0], crossover_bloc_size[1])
            cross_ordres.append(ordre.crossover_2_parents(best_ordres[parents[0]], best_ordres[parents[1]], bloc_size))
        # evaluations
        population = best_ordres + mutated_ordres + cross_ordres
        scores = ordre.population_eval(population, n_cores, tasks_dict, optimal_time)
        """# selection of the bests
        best_ordres = selection_nbest_mpi(population, n_selected, scores, verbose=verbose)

        if graph_evolution and Me == 0:
            graph_evo_best.append(best_ordres[0])"""
        # legality checking
        if verify_legality:
            for ind in population:
                if not ind.isLegal(tasks_dict, n_tasks):
                    return f'ERROR !!! illegal order thrown at ' + str(ind)
        # time_analytics
        if time_analytics and Me == 0:
            ana_ordres.append(best_ordres[0].ordre)
            ana_scores.append(scores[0])
            ana_means.append(ordre.mean(scores))


    # log results to the console
    best_result = selection_nbest_mpi(population, NbP, scores)[0]

    if Me == 0:
        bar = '\n_______________________'
        print('\n' + bar + '\n____________RESULTS__________' + bar + '\n')
        print('the best ordre has a score of : ', ordre.population_eval([best_result], n_cores,tasks_dict, optimal_time)[0])
        print(bar + '\n\n')
        print(keep_best_result_azure)


        # time_analytics score printing
        if time_analytics:
            analysis.performance_evaluation(ana_scores, ana_means)

        """# blanks analysis
        if blank_analysis:
            analysis.blank_analysis(best_result.CPUScheduling(n_cores, tasks_dict)[1])"""

        # graph printing
        if colored_graph_displaying:
            printgraph.print_color_graph(tasks_dict, best_result)

        # graph evolution
        if graph_evolution:
            pos = printgraph.getpos(tasks_dict)
            for i in range(epochs):
                printgraph.print_color_graph(tasks_dict, graph_evo_best[i], pos=pos, title=f'best at epoch {i}')

    if Me == 0:
        return best_result
    else:
        return None


# graph to use
data_folder = Path("../graphs")
path_graph = data_folder / "mediumComplex.json"
data_folder = Path("/mnt/batch/tasks/shared/code") # for Azure
path_graph = data_folder / "largeComplex.json"
#path_graph = "/code/mediumComplex.json"

# sizes
n_population = 20
n_cores = 4
# generation : sum must be equal to n_population
# n_selected is the number of best individuals kept between each iteration, same idea for n_mutated and n_crossed
n_selected = 3
n_mutated = 4
n_crossed = 3
# genetics --> adapt the blocs size and the mutation numbers to the number of tasks
mutations_prob = 0.6
nb_mut_max = 100000
crossover_bloc_size = (10000, 100000)  # must be inferior to n_tasks
# execution
epochs = 20
# logs during the execution?
verbose = True
time_analytics = True
colored_graph_displaying = False
blank_analysis = False
verify_legality = False
graph_evolution = False
dict_ordres=[]
comm = MPI.COMM_WORLD
NbP = comm.Get_size()
Me = comm.Get_rank()
if verbose:
    print("Initialization of process ", Me, "/", NbP)
comm.Barrier()

if __name__ == "__main__":
    # START ALGO   
    if Me == 0:
        start_time = time()
    best_result = main_genetics(path_graph, n_population, n_cores, n_selected, n_mutated, n_crossed, mutations_prob,
                                nb_mut_max, crossover_bloc_size, epochs, verbose=verbose, time_analytics=time_analytics,
                                colored_graph_displaying=colored_graph_displaying, blank_analysis=blank_analysis,
                                verify_legality=verify_legality, graph_evolution=graph_evolution)
    if Me == 0:
        end_time = time()
        print('Total Time : {0} s'.format(end_time - start_time)) 