class TimeTask:
    def __init__(self, heure, minute ,seconde , ms):
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


def getTimeFromData(data):
    # data form is hh:mm:ss.sssssss STRING
    data = data.replace('.',':')
    list = data.split(':')
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
    max = TimeTask(0, 0, 0, 0)
    for i in times:
        if max.isSmaller(i):
            max = i
    return max
