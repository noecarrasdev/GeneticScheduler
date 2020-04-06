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
    global comm, NbP, Me
    n_taches = len(population[0].ordre)
    d=int(np.log2(NbP)) #diMension du cube
    tab_inf = None
    tab_sup = None
    pivot = None
    dtype=[("individu", ordre.Ordre),("score",float)]  #type qu'on va utiliser pour trier avec np.sort
    data = []

    n_pop = len(population)

    if n > n_pop * NbP:
        return 'error : you tried to select more nodes that there is in the population'
     
    """    Partie avec scatter et gather
    score_gather = comm.gather(scores, 0)
    population_gather = comm.gather(population, 0)

    if Me == 0:
        if verbose:
            best_scores = [None] * n
        best_elements = [None] * n
        score_gather = np.array(score_gather)
        score_ranks = sorted(np.ndindex((NbP, n_pop)),
                             key=lambda i: score_gather[i])  # indexes of the biggest indexes in decreasing order
        for i in range(n):
            best_elements[i] = population_gather[score_ranks[i][0]][score_ranks[i][1]]
            if verbose:
                best_scores[i] = score_gather[score_ranks[i]]
        if verbose:
            print('best is : ', best_scores[0])
            print('average is : ', np.mean(best_scores))
        best_elements = np.array(best_elements).reshape(NbP, n // NbP)
    else:
        best_elements = None
    best_elements = comm.scatter(best_elements, 0)
    if Me == 0 
        return list(best_elements)"""
    
    def binary2int(tab) :
        res = 0
        for i in range(len(tab)) :
            res+=(2**i)*tab[i]
        return(res)

    def int2binary(n) :
        bin = np.binary_repr(int(n))
        res = np.zeros(d)
        for i in range(len(bin)) :
            res[i] = (bin[i])
        return(res)

    def separation_pop_score(tab) :
        """pour séparer lpop et socre pour l'envoie en MPI"""
        n=len(tab)
        if n==0 :
            return (np.empty(0),np.empty(0))
        else :
            res1=[]
            res2 = []
            for i in range(n) :
                if tab[i][0]  :
                    res1.append(tab[i][0].ordre)              #on garde le type array parce que ordre MPI arrive pas
                    res2.append(tab[i][1])
            return(np.array(res1),np.array(res2))

    def reunion_pop_score(tab_pop,tab_score) :
        """pour réunir pop et score en une table"""
        n = len(tab_pop)
        if n == 0 : 
            return(np.empty(0))
        else :
            res=[]
            for i in range(n) :
                if tab_pop[i] :
                    res.append((tab_pop[i],tab_pop[i]))
            return(np.array(res))
    
    def tab2ordre(tab) :
        res=[]
        for i in tab :
            res.append(Ordre(i))
        return res 



    
    def partition(tab,x) :
        """separer la liste en 2 liste une dont les individus avec un score <x et lautres >x"""
        tab_i=[]
        tab_s=[]
        for k in tab :
            if k[1] : 
                if k[1]<x :
                    tab_i.append(k)
                else :
                    tab_s.append(k)
            return(np.array(tab_i,dtype=dtype),np.array(tab_s,dtype=dtype))
    

    """on effectue le tri rapide sur hypercube en simultané sur tous les coeurs"""
    for i in range(len(population)) :    #creation de liste regroupant la population et score
        data.append((population[i],scores[i]))         
    data = np.array(data,dtype=dtype)    #on type l'array pour le trier
    
    print(data)
    data = np.sort(data, order="score")    # on trie sur les scores, tri initial 
    for i in range(d-1,-1,-1) :
        if np.all(np.equal(int2binary(Me)[:i+1],np.zeros(i))) :            #choix des coeurs qui donneront un pivot
            m=len(data)
            pivot = data[m//2][1]                         #on prend la mediane en pivot
            for j in range(2**(i+1)-1) :                   #on envoie le pivot aux coeurs qui ne calculerons pas de pivot
                comm.ibsend(pivot,Me+j+1)
                print("Sent : From {} to {}".format(Me, Me+j+1))
        else : 
            target = np.copy(int2binary(n))        #sinon on prend le pivot du coeurs associé
            for j in range(i) :
                target[j] = 0
            target = binary2int(target)
            pivot = comm.irecv(source=target)
            print("Received : From {} to {}".format(target, Me))

        tab_inf,tab_sup = partition(data,pivot)        #on partitionne en fonction du pivot
        if int2binary(Me)[i] ==0 :
            target = np.zeros(d)                               #calcul de la target avec qui on va échanger les listes
            target[i] = 1
            target = target + int2binary(Me)
            target = binary2int(target)
            numData=len(tab_sup)                    #on envoie et recupere le nombre de donnees a envoyer ou recvoir
            comm.ibsend(numData,dest=target)
            print("Sent : From {} to {}".format(Me, target))
            numData_rec = comm.irecv(source=target)
            print("Received : From {} to {}".format(target, Me))
            tab_buf_pop = np.empty((numData_rec,n_taches))
            tab_buf_scores = np.empty(numData_rec)

        else :
            target = np.zeros(d)
            target[i] = 1
            target = int2binary(Me)-target 
            target = binary2int(target)
            numData=len(tab_inf)
            comm.ibsend(numData,dest=target)
            print("Sent : From {} to {}".format(Me, target))
            numData_rec= comm.irecv(source=target)
            print("Received : From {} to {}".format(target, Me))
            tab_buf_pop = np.empty((numData_rec,n_taches))
            tab_buf_scores = np.empty(numData_rec)
        
        if int2binary(Me)[i] ==0 :
            tab_sup_pop,tab_sup_score = separation_pop_score(tab_sup)                  #on envoie/recoit les donnees de population et score
            comm.ibsend(tab_sup_pop,dest=target)
            print("Sent : From {} to {}".format(Me, target))
            comm.ibsend(tab_sup_score,dest = target)
            print("Sent : From {} to {}".format(Me, target))
            comm.irecv(tab_buf_pop,source=target)
            print("Received : From {} to {}".format(target, Me))
            comm.irecv(tab_buf_scores,source=target)
            print("Received : From {} to {}".format(target, Me))
            tab_buf_pop = tab2ordre(tab_buf_pop)                 #on repasse sur un ordre
            tab_buf = np.array(reunion_pop_score(tab_buf_pop,tab_buf_scores),dtype=dtype)
            data = np.sort(np.concatenate((tab_inf,tab_buf)),order = "score")    #on fait l'union des deux liste en ordonnant
        else :
            tab_inf_pop,tab_inf_score = separation_pop_score(tab_inf)                  #on envoie/recoit les donnees
            comm.ibsend(tab_inf_pop,dest=target)
            print("Sent : From {} to {}".format(Me, target))
            comm.ibsend(tab_inf_score,dest=target)
            print("Sent : From {} to {}".format(Me, target))
            comm.irecv(tab_buf_pop,source=target)
            print("Received : From {} to {}".format(target, Me))
            comm.irecv(tab_buf_scores,source=target)
            print("Received : From {} to {}".format(target, Me))
            tab_buf_pop = tab2ordre(tab_buf_pop)         
            tab_buf = np.array(reunion_pop_score(tab_buf_pop,tab_buf_scores),dtype=dtype)
            data = np.sort(np.concatenate((tab_sup,tab_buf)),order = "score")    #on fait l'union des deux liste en ordonnant
    if Me == 0 :
        best_elements = [k[0].ordre for k in data]   #on recupere uniquement les individus en array sans les scores
        if len(best_elements)>n :     #on prend que les n meilleurs si jamais on en a trop 
            best_elements = best_elements[:n]
        numDatasend_bcast = len(best_elements)
    comm.bcast(numDatasend_bcast,0)

    if Me != 0 : 
        best_elements = np.empty(numDatasend_bcast*n_taches,dtype='d')
    comm.Bcast(best_elements,0)
    best_elements = tab2ordre(best_elements) #on repasse avec des ordre
    if Me == 0 :
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

    # execution
    for epoch in range(epochs):
        if verbose and Me == 0:
            print(f'\n__________epoch n{epoch}_________')
        # selection of the bests
        best_ordres = selection_nbest_mpi(population, n_selected, scores, verbose=verbose)

        if graph_evolution and Me == 0:
            graph_evo_best.append(best_ordres[0])
        # mutations
        mutated_ordres = []
        for _ in range(n_mutated // NbP):
            add_index = np.random.randint(0, n_selected // NbP, 1)[0]
            mutated_ordres.append(best_ordres[add_index].mutation_multiple_out(nb_mut_max, mutation_prob, tasks_dict))
        # crossovers
        cross_ordres = []
        for _ in range(n_crossed // NbP):
            parents = np.random.randint(0, n_selected // NbP, 2)
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
# data_folder = Path("/mnt/batch/tasks/shared/GeneticScheduler/graphs") # for Azure
path_graph = data_folder / "smallRandom.json"
#path_graph = "/code/mediumComplex.json"

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
crossover_bloc_size = (2, 8)  # must be inferior to n_tasks
# execution
epochs = 10
# logs during the execution?
verbose = True
time_analytics = True
colored_graph_displaying = False
blank_analysis = False
verify_legality = False
graph_evolution = False

comm = MPI.COMM_WORLD
NbP = comm.Get_size()
Me = comm.Get_rank()
if verbose:
    print("Initialization of process ", Me, "/", NbP)
comm.Barrier()

if __name__ == "__main__":
    # START ALGO
    print("commence")
    if Me == 0:
        start_time = time()
    best_result = main_genetics(path_graph, n_population, n_cores, n_selected, n_mutated, n_crossed, mutations_prob,
                                nb_mut_max, crossover_bloc_size, epochs, verbose=verbose, time_analytics=time_analytics,
                                colored_graph_displaying=colored_graph_displaying, blank_analysis=blank_analysis,
                                verify_legality=verify_legality, graph_evolution=graph_evolution)
    if Me == 0:
        end_time = time()
        print('Total Time : {0} s'.format(end_time - start_time))