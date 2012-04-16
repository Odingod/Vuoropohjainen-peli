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
        Resources.__init__(self, "gold", "gold_20x20.png")
        