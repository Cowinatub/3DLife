import time
import map
from sharedMemory import SharedState

class Time:
    def __init__(self, innitialMap, rules, frequency=10, timeStatesToDisplay=1):
        self.rules = []
        self.nTimeDimensions = 0
        self.turnN = 0
        self.lastFrameTime = time.time()
        self.frequency = frequency
        self.running = False
        self.drawMode = False
        self.timeStatesToDisplay = timeStatesToDisplay

        try:
            for rule in rules:
                self.rules.append(rule)
                self.nTimeDimensions = self.nTimeDimensions + 1
        except TypeError:
            self.rules.append(rules)
            self.nTimeDimensions = 1

        self.spaceDimensions = innitialMap.dimensions
        self.maps = [innitialMap]
        currentmap = self.maps
        for i in range(0, self.nTimeDimensions - 1):
            currentmap[0] = [innitialMap]
            currentmap = currentmap[0]

        # create shared memory for C++ integration
        self.sharedState = SharedState(self.spaceDimensions, timeStatesToDisplay)

    def setDrawMode(self, mode:bool):
        self.drawMode = mode

    def changeFrequency(self, frequency):
        self.frequency = frequency

    def update(self, properties={}):
        currentTime = time.time()
        dt = currentTime - self.lastFrameTime
        if self.running:
            if dt > 1/self.frequency:
                self.step(properties)

    def step(self, properties={}):
        self.lastFrameTime = time.time()
        self.processTurn()
        maps = self.getMaps()
        passmaps = []
        for i in range(0, self.timeStatesToDisplay):
            index = self.turnN - self.timeStatesToDisplay + i + 1
            if index > 0:
                passmaps.append(maps[index].map)
            else:
                emptyMap = map.Map(self.spaceDimensions, self.maps[0].wrap, 0)
                passmaps.append(emptyMap.map)


        # write state to shared mem
        self.sharedState.update(passmaps, self.drawMode)

        # print(self.timeStatesToDisplay)
        if 'draw' in properties:
            if len(self.spaceDimensions) == 1:
                maps[self.turnN].print1D()
            elif len(self.spaceDimensions) == 2:
                maps[self.turnN].print2D()
            elif len(self.spaceDimensions) == 3:
                maps[self.turnN].print3D()

    def run(self):
        self.running = True

    def pause(self):
        self.running = False

    def processTurn(self):
        self.processTurnAux(self.maps, 0, 0)
        self.turnN = self.turnN + 1

    def processTurnAux(self, map, rulei, depth):
        if depth < self.nTimeDimensions:
            lastMap = map[len(map) - 1]
            map.append(self.rules[rulei].processMap(lastMap))
            for nextmap in map:
                self.processTurnAux(nextmap, rulei + 1, depth + 1)

    def getMaps(self):
        return self.maps

    def getTurnN(self):
        return self.turnN

    def exportInfo(self):
        timeArray = self.iterateTime(self.maps)
        return [timeArray, self.turnN]

    def getLatestMapFirstD(self):
        return self.maps[self.turnN].exportInfo()

    def iterateTime(self, time):
        if isinstance(time, list):
            timeArray = []
            for dimension in time:
                timeArray = timeArray + self.iterateTime(dimension)
            return timeArray
        else:
            return time.exportInfo()