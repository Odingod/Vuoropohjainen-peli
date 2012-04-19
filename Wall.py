'''
Created on 6.3.2012

@author: Teemu
'''
import Players
from Units import *
import Map
from PySide.QtGui import QImage

class Wall(Building):
    def __init__(self, name, image="wall_30x30.png", tile=None,
            population=0, owner=None, map=None):
        Building.__init__(self, 'wall', QImage(image), tile, [], 100, owner=owner)
        self.tile = tile
        self.map = map

    def build(self, building):
        print "wall can't build a thing"
	return False