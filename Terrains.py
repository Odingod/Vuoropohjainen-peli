from PySide.QtGui import QImage

class Terrain(object):
    def __init__(self,id,image):
        self.id=id
        self.canHoldUnit = True
        self.image=image
        
class Ground(Terrain):
    def __init__(self):
        Terrain.__init__(self, 'ground', QImage('earth.png'))
        
class Water(Terrain):
    def __init__(self):
        Terrain.__init__(self, 'water', QImage('water.png'))
        self.canHoldUnit = False