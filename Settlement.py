'''
Created on 6.3.2012

@author: Teemu
'''
import Players
from Units import *
import Map
from PySide.QtGui import QImage

class Settlement(Building):
    def __init__(self, name='Random Settlement', image="castle_30x30.png", tile=None,
            population=1000, owner=None, map=None):
        Building.__init__(self, 'settlement', QImage(image), tile, moves=[], hp=100, owner=owner)
        self.population = population
        self.main_building = 1
        self.barracks = 0
        self.tile = tile
        self.map = map

    def build(self, building):
        if building == "barracks":
            self.barracks += 1
        elif building == "farm":
            self.population += 100 
            print "Farm has been built. Population is now", self.population
        elif building == "wall":
            self.hp += 50
        else:
            print "no such building, available buildings: barracks, farm, wall"
            return False

        self.owner.unitDone()
        return True

    def do_recruit(self, type, owner, tile, price):
        if self.owner.treasury < price:
            print 'Not enough gold. You have {0} and need {1}'.format(
                    self.owner.treasury, price)
            return False

        unit = type(owner=owner, tile=tile)
        tile.addUnit(unit)
        self.owner.unitCount += 1
        self.owner.treasury -= price
        print 'Your treasury has now {0} gold.'.format(self.owner.treasury)
        return True

    def recruit(self, unit):
        neighbors = self.tile.getBoardNeighbors()
        types = {
            'tank': Tank,
            'melee': Melee,
            'ranged': Ranged,
            'builder': Builder,
        }
        prices = {
            'tank': 200,
            'ranged': 125,
            'melee': 75,
            'builder': 25,
        }

        for x, y in neighbors:
            tile = self.map.tiles[x][y]

            if tile.canBuild() and tile.terrain.canHoldUnit and \
                    len(tile.units) == 0:
                if not self.do_recruit(types[unit], self.owner, tile,
                        prices[unit]):
                    return False

                self.owner.unitDone()
                return True

        print 'Cannot recruit - no empty tiles.'
        return False
