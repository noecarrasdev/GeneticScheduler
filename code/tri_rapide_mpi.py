from mpi4py import MPI 
import numpy as np 
from math import *

"""j'ai pas trop commenté parce que j'ai juste suivi les etapes qui sont exposées dans le cours chap2.5 hypercube quicksort version 2"""

comm=MPI.COMM_WORLD
NbP = comm.Get_size()
me = comm.Get_rank()

def choix_pivot(tab) :
    """choix du pivot median dans une liste """
    tab=np.sort(tab)
    n=len(tab)
    return(tab[n//2])


def quick_sort_hypercube(tab) :
    d=int(np.log2(NbP))
    n = len(tab)
    n_sub = n//NbP
    r=n%NbP
    data = None
    tab_inf = None
    tab_sup = None
    tab_buf = None
    pivot = None
    indice_pivot = None
    res = []
    """ on reparti la liste sur les différents processeur"""
    if me <= r :
        data = np.concatenate((tab[n_sub*me:n_sub*(me+1)],tab[-(me+1)]))
    else :
        data = tab[n_sub*me:n_sub*(me+1)]
    np.sort(data)
    for i in range(d-1,-1,-1) :
        pivot = choix_pivot(data)        #j'ai limpresion cette ligne sert a rien vu qu'on trie genre wtf 
        indice_pivot = data.index(pivot) #celle la aussi 
        np.partition(data,indice_pivot)  #celle la aussi 
        n = len(data)
        tab_inf = data[:ceil(n/2)]
        tab_sup = data[ceil(n/2):]
        if np.binary_repr(me)[i] ==0 :
            target = np.zeros(d)
            target[i] = 1
            target = target + me 
            comm.send(tab_sup,target)
            comm.recv(tab_buf,target)
            data = np.sort(np.concatenate((tab_inf,tab_buf)))   #c'est le union_ordonne mais je suis pas 100% sur que c'est ca
        else :
            target = np.zeros(d)
            target[i] = 1
            target = me-target 
            comm.send(tab_inf,target)
            comm.recv(tab_buf,target)
            data = np.sort(np.concatenate((tab_sup,tab_buf)))
    for i in range(NbP) :      #on reconcatene le tout dans l'ordre 
        if me == i :
            res = np.concatenate((res,data))
    return res




