'''
Created on 6.3.2012

@author: Teemu
'''
import Players
import Units
import Map
from PySide.QtGui import QImage
class Settlement():
    def __init__(self, name, image=QImage("castle_30x30.png"), tile=None, population=1000, owner=None):
        self.name = name
        self.owner = owner
        self.image = image
        self.tile = tile
        self.population = population
        self.main_building = 1
        self.barracks = 0
    def build(self, building):
        if building == "barracks":
            self.barracks += 1
        else:
            print "no such building, available buildings: barracks"
    def recruit(self, unit):
        if unit == "tank":
            unit = Units.Tank(owner=self.owner)
            self.tile.addUnit(unit)
            
    
    