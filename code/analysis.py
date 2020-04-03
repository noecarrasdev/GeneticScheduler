import numpy as np
import matplotlib.pyplot as plt
import time_personalized as tmpz
import ordre

# CODE

def performance_evaluation(scores, means):
    '''
    :param scores: list of scores
    :param means:  list of mean scores
    :return: void, displays figure on performances according to epochs
    '''
    plt.figure()
    n = len(scores)
    abs = np.linspace(1, n, num=n)
    plt.plot(abs, np.array(scores), label='best')
    plt.plot(abs, np.array(means), label='means')
    plt.xlabel("EPOCH")
    plt.ylabel("SCORE : time scheduled / optimal time")
    plt.legend()
    plt.show()

# TEST LAUNCH
if __name__ == "__main__":
    scores = [1.01, 1.001, 1.0001, 1.000079]
    means = [1.02, 1.027, 1.00065, 1.00025]
    performance_evaluation(scores, means)
