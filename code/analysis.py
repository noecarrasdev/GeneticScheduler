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


def blank_analysis(cpuord):
    '''
    :param cpuord: [[(task, begintime), ...] * n_cores]
    :return: logs analysis on the blanks
    '''
    blanks = []
    for core in cpuord:
        current = tmpz.TimeTask(0, 0, 0, 0)
        for task in core:
            blank = task[1].tomsecond() - current.tomsecond()
            if blank:
                blanks.append(blank)
            current = task[0].time.add(task[1])

    # ANALYSIS PRINTING
    number_blanks = len(blanks)
    if number_blanks > 0:
        print(f'there was {number_blanks} during this sequence')
        mean_b = ordre.mean(blanks)
        print(f'the mean size of the blanks is {mean_b} milliseconds')
        stdev = ordre.mean([(blank - mean_b) ** 2 for blank in blanks]) ** (1/2)
        print(f'the standard deviation is of {stdev} milliseconds')
        sorted_b = sorted(blanks)
        print(f'the biggest blanks are {sorted_b[-(int(0.1*number_blanks)):]} milliseconds')
        print(f'the minimum size if {sorted_b[0]} milliseconds')
    else:
        print('no blanks were found...')


# TEST LAUNCH
if __name__ == "__main__":
    scores = [1.01, 1.001, 1.0001, 1.000079]
    means = [1.02, 1.027, 1.00065, 1.00025]
    performance_evaluation(scores, means)
