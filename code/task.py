import time_personalized as tmpz


# CODE

class Task:
    def __init__(self, ID, time, dependence):
        '''
        :param ID: Integer corresponding to the task number
        :param time: TimeTask object
        :param dependence: list of integers (Tasks ID parameters)
        '''
        self.ID = ID
        self.time = time
        self.dependence = dependence


# TEST LAUNCH
if __name__ == "__main__":
    task1 = Task(1, tmpz.TimeTask(1, 3, 6, 18), [])
    print(task1)
    # see if it throws an error