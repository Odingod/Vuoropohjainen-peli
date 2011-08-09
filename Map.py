from Hexagon import *
from Units import *
from random import choice, randint

class Map(object):
    def __init__(self):
        self.tiles = []
        self.metrics = Hexagon(-1, -1)
        self.waitingInput = []
        self.units = []
    
    def createSquareMap(self, numUnits, players, w=10, h=10, r=20):
        self.metrics = Hexagon(-1, -1, r)
        for i in xrange(w):
            self.tiles.append([])
            for j in xrange(h):
                self.tiles[i].append(Tile(i, j, r, self, Ground() if randint(1, 10) < 9 else Water()))
        for i in xrange(numUnits):
            for player in players:
                while True:
                    #tile = choice(choice(self.tiles))
                    row = choice(self.tiles)
                    tile = choice(row)
                    if tile.terrain.canHoldUnit and not tile.units:
                        unit = Tank(owner=player)
                        tile.addUnit(unit)
                        self.units.append(unit)
                        break

    
    def getHexAt(self, x, y):
        i_t = x / self.metrics.s
        j_t = int(floor((y - (i_t % 2) * self.metrics.h / 2) / self.metrics.h))
        x_t = x - i_t * self.metrics.s
        y_t = (y - (i_t % 2) * self.metrics.h / 2) - j_t * self.metrics.h
        d_j = 1 if y_t > self.metrics.h / 2 else 0
        if x_t > self.metrics.r * abs(1. / 2. - y_t / self.metrics.h):
            return (i_t, j_t)
        else:
            return (i_t - 1, j_t - (i_t - 1) % 2 + d_j)
    
    def tellClick(self, i, j):
        if self.waitingInput:
            temp = self.waitingInput
            self.waitingInput = []
            for action in temp:
                action(i, j)
            

    def addAction(self, action):
        self.waitingInput.append(action)

