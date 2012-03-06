from PySide.QtGui import QImage

class Terrain(object):
    def __init__(self, id, image):
        self.id = id
        self.canHoldUnit = True
        self.image = image

    def __saveable__(self):
        d = {}

        d['id'] = self.id
        d['canHoldUnit'] = self.canHoldUnit

        return d

    @classmethod
    def __load__(cls, d):
        if d['id'] == 'ground':
            t = Ground()
        elif d['id'] == 'water':
            t = Water()

        t.canHoldUnit = d['canHoldUnit']

        return t
        
class Ground(Terrain):
    def __init__(self):
        Terrain.__init__(self, 'ground', QImage('earth.png'))
        
class Water(Terrain):
    def __init__(self):
        Terrain.__init__(self, 'water', QImage('water.png'))
        self.canHoldUnit = False
