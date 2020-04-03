# CODE

class TimeTask:
    def __init__(self, heure, minute ,seconde , ms=0):
        self.heure = heure
        self.minute = minute
        self.seconde = seconde
        self.ms = ms

    def add(self, t2):
        nms = (self.ms + t2.ms)%100
        secondeTrop = (self.ms + t2.ms)//100
        nseconde = (self.seconde + t2.seconde + secondeTrop)%60
        minuteTrop = (self.seconde + t2.seconde + secondeTrop)//60
        nminute = (self.minute + t2.minute + minuteTrop)%60
        heureTrop = (self.minute + t2.minute + minuteTrop)//60
        nheure = (self.heure + t2.heure + heureTrop)
        return TimeTask(nheure, nminute, nseconde, nms)

    def __str__(self):
        return str(self.heure) + ":" + str(self.minute) + ":" + str(self.seconde) + ":" + str(self.ms)

    def isSmaller(self, t2):
        if self.heure < t2.heure:
            return True
        elif self.heure > t2.heure:
            return False
        elif self.minute < t2.minute:
            return True
        elif self.minute > t2.minute:
            return False
        elif self.seconde < t2.seconde:
            return True
        elif self.seconde > t2.seconde:
            return False
        elif self.ms < t2.ms:
            return True
        else :
            return False

    def tomsecond(self):
        seconds = 0
        seconds += self.ms
        seconds += self.seconde * 1000
        seconds += self.minute * 1000 * 60
        seconds += self.heure * 1000 * 60 * 60
        return seconds


def getTimeFromData(data):
    # data form is hh:mm:ss.sssssss STRING
    data = data.replace('.',':')
    list = data.split(':')
    if len(list)==3:
        return TimeTask(int(list[0]), int(list[1]), int(list[2]))
    else:
        return TimeTask(int(list[0]), int(list[1]), int(list[2]), int(list[3][:2]))


def argmini(times):
    '''
    :param times: list of Times
    :return: the index of the smallest time
    '''
    minTime = times[0]
    minCore = 0

    for i in range(len(times)):
        if times[i].isSmaller(minTime):
            minTime = times[i]
            minCore = i
    return minCore


def maxTime(times):
    '''
    :param times: list of TimeTask
    :return: the bigger time
    '''
    max = TimeTask(0, 0, 0, 0)
    for i in times:
        if max.isSmaller(i):
            max = i
    return max

def metric_ratio(over, under):
    '''
    :param over: TimeTask
    :param under: TimeTask
    :return: float corresponding to the time ratio
    '''
    return over.tomsecond()/under.tomsecond()


# TEST LAUNCH
if __name__ == "__main__":
    time1 = TimeTask(0,1,2,300)
    time2 = TimeTask(1,2,6,700)
    time3 = time1.add(time2)
    time4 = TimeTask(0,0,0,1)
    print('time 1 : ', time1)
    print('time 2 : ', time2)
    print('time 3 (t1+t2) : ', time3)
    print('test inequalities, true statement : ', time1.isSmaller(time2))
    print('test tomsecond : return 62300 : ', time1.tomsecond())
    print('test tomsecond : return 1 : ', time4.tomsecond())
    print('should return time1 index ie 0 : ', argmini([time1, time2, time3]))
    print('should return time3 as TimeTask : ', maxTime([time1, time2, time3]))
