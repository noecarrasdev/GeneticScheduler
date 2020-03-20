import json
import task
import time_personalized 


def loadTasks(doc):
    '''
    :param doc: path of a proper JSON file
    :return: a Dictionnary with the tasks ID, time and dependancies
    '''
    tasks = {}
    with open(doc) as f:
        data = json.load(f)
        for key, value in data["nodes"].items():
            tasks[int(key)] = task.Task(int(key), time_personalized.getTimeFromData(value["Data"]), value["Dependencies"])
    return tasks

def ideal_time(dict):
    '''
    :param dict: dictionnary issued from loadTasks function
    :return: the best time achievable (often non realistic due to the dependencies)
    '''
    total = time_personalized.TimeTask(0, 0, 0, 0)
    for key in dict.keys():
        total = total.add(dict[key].time)
    return total


# TEST LAUNCH
testLaunch = True


# TEST
if testLaunch:
    document = '../graphs/smallRandom.json'
    tasksDict = loadTasks(document)
    print(tasksDict)
    total_max = ideal_time(tasksDict)
    print(total_max)
    # see if it gets an error or an unusual object