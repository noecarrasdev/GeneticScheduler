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
            tasks[int(key)] = task.Task(int(key), time_personalized.getTimeFromData(value["Data"]),
                                        value["Dependencies"])
    # this is useful to take the complex graphs that starts with ID greater than 1 and bring them back to the same scheme as the Random.json graphs.
    keys = sorted(tasks.keys())
    first = keys[0]
    if first != 1:
        for key in keys:
            tasks[key + 1 - first] = tasks[key]
            newdep = []
            for dep in tasks[key + 1 - first].dependence:
                newdep.append(dep - first + 1)
            tasks[key + 1 - first].dependence = newdep
            del tasks[key]
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
if __name__ == "__main__":
    document = '../graphs/smallRandom.json'
    tasksDict = loadTasks(document)
    print(tasksDict)
    total_max = ideal_time(tasksDict)
    print(total_max)
    # see if it gets an error or an unusual object