'''
Created on 6.3.2012

@author: Teemu
'''
import Players
from Units import *
import Map
from PySide.QtGui import QImage

class Settlement(Unit):
    def __init__(self, name, image="castle_30x30.png", tile=None,
            population=1000, owner=None, map=None):
        Unit.__init__(self, 'settlement', QImage(image), tile, [], 100, owner)
        self.population = population
        self.main_building = 1
        self.barracks = 0
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

    def recruit(self, unit):
        if unit == "tank":
            if self.population > 1500:
                unit = Tank(owner=self.owner)
                self.tile.addUnit(unit)
                self.map.units.append(unit)
            unit = Tank(owner=self.owner)
            self.tile.addUnit(unit)
            self.map.units.append(unit)
