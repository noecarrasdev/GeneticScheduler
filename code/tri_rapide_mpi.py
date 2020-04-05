from mpi4py import MPI 
import numpy as np 
from math import *
import ordre

"""j'ai pas trop comMenté parce que j'ai juste suivi les etapes qui sont exposées dans le cours chap2.5 hypercube quicksort version 2"""

comm=MPI.COMM_WORLD
NbP = comm.Get_size()
Me = comm.Get_rank()
d=int(np.log2(NbP)) #diMension du cube
data = np.empty(0)
tab_inf = None
tab_sup = None
tab_buf = None
pivot = None
indice_pivot = None
dtype=[("individu" = ordre.Ordre),("score"=float)]     #pour pouvoir avoir l'inidividu et son score a la fois


def binary2int(tab) :
    res = 0
    for i in range(len(tab)) :
        res+=(2**i)*tab[i]
    return(res)

def int2binary(n) :
    bin = np.binary_repr(n)
    res = np.zeros(len(bin))
    for i in range(len(bin)) :
        res[i] = int(bin[i])
    return(res)



def choix_pivot(n,i) :
    """choix du pivot Median dans une liste du coup on prend """
    
    if int2binary(n)[:i+1]==[0]*i :            #on prend comMe pivot la Medianne
        n=len(data)
        return(data[n//2][1])
    else :
        target = np.copy(int2binary(Me))        #sinon on prend le pivot du coeurs associé
        for j in range(i) :
            target[j] = 0 
        target = binary2int(target)
        return(choix_pivot(target,i))

def partition(tab,x) :
    """separer la liste en 2 liste une dont les individus avec un score <x et lautres >x"""
    tab_i=[]
    tab_s=[]
    for k in tab :
        if k[1]<x :
            tab_i.append(k)
        else :
            tab_s.append(k)
    return(tab_i,tab_s)


def quick_sort_hypercube(tab) :
    n = len(tab)
    n_sub = n//NbP
    r=n%NbP
    
    res = []
    """ on reparti la liste sur les différents processeur"""
    if Me <= r :
        data = np.concatenate((tab[n_sub*Me:n_sub*(Me+1)],tab[-(Me+1)]))
    else :
        data = tab[n_sub*Me:n_sub*(Me+1)]
    np.sort(data,order="score")    # on trie sur les scores
    for i in range(d-1,-1,-1) :
        pivot = choix_pivot(Me,i)         
        tab_inf,tab_sup = partition(data,pivot)  
        if int2binary(Me)[i] ==0 :
            target = np.zeros(d)                               #calcul de la target avec qui on va échanger les listes
            target[i] = 1
            target = target + int2binary(Me)
            target = binary2int(target)
            comm.send(tab_sup,target)
            comm.recv(tab_buf,target)
            data = np.sort(np.concatenate((tab_inf,tab_buf)),order = "score")   #c'est le union_ordonne mais je suis pas 100% sur que c'est ca
        else :
            target = np.zeros(d)
            target[i] = 1
            target = int2binary(Me)-target 
            target = binary2int(target)
            comm.send(tab_inf,target)
            comm.recv(tab_buf,target)
            data = np.sort(np.concatenate((tab_sup,tab_buf)),order = "score")





