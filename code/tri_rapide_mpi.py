from mpi4py import MPI 
import numpy as np 
from math import *

"""j'ai pas trop commenté parce que j'ai juste suivi les etapes qui sont exposées dans le cours chap2.5 hypercube quicksort version 2"""

comm=MPI.COMM_WORLD
NbP = comm.Get_size()
me = comm.Get_rank()
d=int(np.log2(NbP)) #dimension du cube
data = np.empty()
tab_inf = None
tab_sup = None
tab_buf = None
pivot = None
indice_pivot = None

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
    """choix du pivot median dans une liste du coup on prend """
    
    if int2binary(n)[:i+1]==[0]*i :            #on prend comme pivot la medianne
        n=len(data)
        return(data[n//2])
    else :
        target = np.copy(int2binary(me))        #sinon on prend le pivot du coeurs associé
        for j in range(i) :
            target[j] = 0 
        target = binary2int(target)
        return(choix_pivot(target,i))

def partition(tab,x) :
    """separer la liste en 2 liste une dont les elemens <x et lautres >x"""
    tab_i=[]
    tab_s=[]
    for k in tab :
        if k<x :
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
    if me <= r :
        data = np.concatenate((tab[n_sub*me:n_sub*(me+1)],tab[-(me+1)]))
    else :
        data = tab[n_sub*me:n_sub*(me+1)]
    np.sort(data)
    for i in range(d-1,-1,-1) :
        pivot = choix_pivot(me,i)         
        tab_inf,tab_sup = partition(data,pivot)  
        if int2binary(me)[i] ==0 :
            target = np.zeros(d)                               #calcul de la target avec qui on va échanger les listes
            target[i] = 1
            target = target + int2binary(me)
            target = binary2int(target)
            comm.send(tab_sup,target)
            comm.recv(tab_buf,target)
            data = np.sort(np.concatenate((tab_inf,tab_buf)))   #c'est le union_ordonne mais je suis pas 100% sur que c'est ca
        else :
            target = np.zeros(d)
            target[i] = 1
            target = int2binary(me)-target 
            target = binary2int(target)
            comm.send(tab_inf,target)
            comm.recv(tab_buf,target)
            data = np.sort(np.concatenate((tab_sup,tab_buf)))
    for i in range(NbP) :      #on reconcatene le tout dans l'ordre 
        if me == i :
            res = np.concatenate((res,data))
    return res




