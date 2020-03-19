import time_personalized as tmpz

class Task:
    def __init__(self, ID, time, dependance):
        '''
        :param ID: Integer corresponding to the task number
        :param time: TimeTask object
        :param dependance: list of integers (Tasks ID parameters)
        '''
        self.ID = ID
        self.time = time
        self.dependance = dependance

# TEST LAUNCH
testLaunch = False

# TEST
if testLaunch:
    task1 = Task(1, tmpz.TimeTask(1, 3, 6, 18), [])
    print(task1)
    # see if it throws an error