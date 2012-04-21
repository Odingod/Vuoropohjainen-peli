'''
Created on 6.3.2012

@author: Teemu
'''
import Players
from Units import *
import Map
from PySide.QtGui import QImage

class Settlement(Building):
    def __init__(self, name, image="castle_30x30.png", tile=None,
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

    def recruit(self, unit):
        if unit == "tank":
            if self.population > 2500:
                unit = Tank(owner=self.owner)
                self.tile.addUnit(unit)
            
            unit = Tank(owner=self.owner)
            print self.tile.getUnit()
            if self.tile.canBuild():
                self.tile.addUnit(unit)
                self.map.units.append(unit)
            else:
                neighbors = self.tile.getBoardNeighbors()
                print neighbors
                for i in range(len(neighbors)):
                    x = neighbors[i][0]
                    y = neighbors[i][1]
                    tile = self.map.tiles[x][y]
                    print tile
                    if tile.canBuild():
                        tile.addUnit(unit)
                        self.map.units.append(unit)
                        self.onwer.unitDone()
                        return True
                print "No empty tiles"
                return False
                    

            self.owner.unitDone()
            return True

        return False
