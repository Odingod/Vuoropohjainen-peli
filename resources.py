'''
Created on 29.3.2012

@author: Teemu
'''
from Units import *
class Resources(Unit):
    def __init__(self, id, image):
        Unit.__init__(self, id, image)
class Gold(Resources):
    def __init__(self):
        Resources.__init__(self, "gold", "raw_gold.png")
class Mine(Building):
    def __init__(self, owner):
        Building.__init__(self, id = "mine", image = "gold_mine.png", owner = owner)
        owner.mine_count += 1
        