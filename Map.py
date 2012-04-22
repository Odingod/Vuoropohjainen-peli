from Hexagon import *
from Units import *
from random import choice, randint
from save import saveable, load
from functools import partial
from Settlement import *
from math import *
from resources import *

class Map(object):
    def __init__(self):
        self.tiles = []
        self.metrics = Hexagon(-1, -1)
        self.waitingInput = []
        self.units = []

    def __saveable__(self):
        d = {}

        d['tiles'] = map(lambda x: map(saveable, x), self.tiles)
        d['metrics'] = saveable(self.metrics)
        d['units'] = map(saveable, self.units)

        return d

    @classmethod
    def __load__(cls, d, game):
        m = cls()
        game.map = m

        m.tiles = map(lambda x: map(partial(load, Tile, game=game), x), d['tiles'])
        m.metrics = load(Hexagon, d['metrics'])

        for t in m.tiles:
            for r in t:
                for u in r.units:
                    m.units.append(u)

        return m

    def makeRandomTileMap(self, depth):
	    if depth == 0:
		    return [[[1,1,1,1,0][random.randrange(0,5)] for y in range(4)] for x in range(4)]
	    oldmap = self.makeRandomTileMap(depth-1)
	    newmap = []
	    for y in range(len(oldmap)):
		    newmap.append( [0] * 2 * len(oldmap) )
		    newmap.append( [0] * 2 * len(oldmap) )
	    for y in range(len(newmap)):
		    for x in range(len(newmap[0])):
			    newmap[x][y] = oldmap[x/2][y/2]
	    #print "mprinting gnemapaw"
	    #for i in newmap:
	    #	print i
	    for y in range(len(newmap)):
		    for x in range( len(newmap[0])):
			    summ = 5
			    tiles = newmap[x][y]
			    if x > 0:
				    tiles += newmap[x-1][y]

			    if y > 0:
				    tiles += newmap[x][y-1]
			    if x < len(newmap[0])-1:
				    tiles += newmap[x+1][y]
			    if y < len(newmap)-1:
				    tiles += newmap[x][y+1]
			    if random.random()*summ > tiles*0.95:
				    newmap[x][y] = 0
			    else:
				    newmap[x][y] = 1
	    return newmap

    def createSquareMap(self, numUnits, players, r=20, size=1):
        h = 2**(size+2)
        w = 2**(size+2)
        self.metrics = Hexagon(-1, -1, r)
        mymap = self.makeRandomTileMap(size)
        print "map randomized"
        if h != len(mymap):
            print "apua, virhe, mappi on vaaran kokoinen :( :S!"
        for i in xrange(w):
            self.tiles.append([])
            for j in xrange(h):
                self.tiles[i].append(Tile(i, j, r, self, Ground() if mymap[i][j] == 1 else Water()))
                self.tiles[i]
        for player in players:
            while True:
                row = choice(self.tiles)
                tile = choice(row)
                if tile.terrain.canHoldUnit and not tile.units:
                    settlement = Settlement("capital", map=self, owner=player, tile=tile)
                    tile.addUnit(settlement)
                    self.units.append(settlement)
                    break
            while True:
                row = choice(self.tiles)
                tile = choice(row)
                if tile.terrain.canHoldUnit and not tile.units:
                    builder = Builder(tile=tile, owner=player)
                    tile.addUnit(builder)
                    self.units.append(builder)
                    break

        for i in xrange(numUnits):
            for player in players:
                while True:
                    row = choice(self.tiles)
                    tile = choice(row)
                    if tile.terrain.canHoldUnit and not tile.units:
                        unit = Tank(owner=player)
                        tile.addUnit(unit)
                        self.units.append(unit)
                        break
        gold_count = 0
        while gold_count < 5:
            row = choice(self.tiles)
            tile = choice(row)
            if tile.terrain.canHoldUnit and not tile.units:
                tile.addUnit(Gold())
                gold_count += 1
                

    
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

