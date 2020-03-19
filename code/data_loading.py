import json
import task
import time_personalized 


def loadTasks(doc):
    '''
    :param doc: path of a proper JSON file
    :return: a Dictionnary with the tasks ID, time and dependancies
    '''
    tasks = []
    with open(doc) as f:
        data = json.load(f)
        for key, value in data["nodes"].items():
            tasks.append(task.Task(int(key), time_personalized.getTimeFromData(value["Data"]), value["Dependencies"]))
    return tasks

# TEST LAUNCH
testLaunch = False

# TEST
if testLaunch:
    document = '../graphs/smallRandom.json'
    tasksDict = loadTasks(document)
    print(tasksDict)
    # see if it gets an error or an unusual object