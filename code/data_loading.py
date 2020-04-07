import json
import task
import time_personalized
from numpy import ceil,inf
import ijson


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
    nodes_dict = {}
    first = keys[0]

    if first != 1:
        n = len(keys)
        for k in range(n):
            nodes_dict[k+1] = tasks[keys[k]]
            nodes_dict[k+1].ID = k+1
            #nodes_dict[key + 1 - first] = nodes_dict[key]
            #nodes_dict[key + 1 - first].ID -= (first - 1)
            newdep = []
            for dep in tasks[keys[k]].dependence:
                newdep.append(keys.index(dep)+1)
            nodes_dict[k+1].dependence = newdep
            del tasks[keys[k]]
        return nodes_dict
    return tasks


def tasksCount(doc):
    '''
    This fuction counts number of tasks in a large JSON file
    '''
    count = 0
    with open(doc, 'r') as f:
        parser = ijson.parse(f)
        for prefix, event, _ in parser:
            if event=='map_key' and prefix=='nodes':
                count += 1
    return count


def loadTasksLargeJson(doc):
    '''
    :param doc: path of a proper large JSON file
    :return: a Dictionnary with the tasks ID, time and dependancies
    '''
    nodes_dict = dict()
    current_key = None
    current_time = None
    current_dependence = list()
    current_reading = False
    current_node_number = 0

    with open(doc, 'r') as f:
        parser = ijson.parse(f)
        for prefix, event, value in parser:
            # Start reading a node :
            if event=='map_key' and prefix=='nodes':
                current_key = value
                current_reading = True
                current_node_number += 1
            if current_reading and current_key!=None:
                if prefix=='nodes.'+current_key+'.Data' and event=='string':
                    current_time = time_personalized.getTimeFromData(value)
                elif prefix=='nodes.'+current_key+'.Dependencies.item' and event=='number':
                    current_dependence.append(value)
                elif prefix=='nodes.'+current_key and event=='end_map':                        
                    nodes_dict[int(current_key)] = task.Task(int(current_key), current_time, current_dependence)
                    current_key = None
                    current_time = None
                    current_dependence = list()
                    current_reading = False
    return nodes_dict


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
    document = '../graphs/largeComplex.json'
    tasksDict = loadTasks(document)
    n = len(tasksDict)
    '''
    for i in range(1, n + 1):
        print(f'individual {i} with ', tasksDict[i].time, ' and dep : ', tasksDict[i].dependence, '\n')
    print(tasksDict)
    total_max = ideal_time(tasksDict)
    print(total_max)
    '''
    for i in range(1, n + 1):
        try:
            foo = tasksDict[i]
            print(tasksDict[i])
        except:
            print(f'problem at {i}')