import numpy as np
import initialisation
import task
import ordre
import data_loading
import time_personalized


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


# appels aux fonctions et paramètres
main()