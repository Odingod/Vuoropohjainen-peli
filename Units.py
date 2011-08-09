from PySide.QtGui import QImage
from PySide.QtCore import QCoreApplication

class Unit(object):
    def __init__(self, id, image, tile=None, moves=(0, 1), hp=30, owner=None):
        self.id = id
        self.image = image
        self.tile = tile
        self.moves = moves
        self.hp = hp
        self.owner = owner
    
    def move(self, i, j):
        tiles = self.tile.map.tiles
        self.tile.removeUnit(self)
        tiles[i][j].addUnit(self)
        #self.tile.setChosenWithNeighbours()
        self.tile.setChosenByDist(-1)
        self.tile.ensureVisible()
        QCoreApplication.instance().processEvents()

        
class Tank(Unit):
    def __init__(self, tile=None, owner=None):
        Unit.__init__(self, 'tank', QImage('alien1.gif'), tile, (1, 2), 25, owner)
    
    def move(self, i, j, fun=None):
        if not self.tile.map.tiles[i][j].chosen:
            print 'You can\'t move that far'
            self.tile.map.addAction(self.move)
        elif self.tile.map.tiles[i][j].terrain.canHoldUnit:
            super(Tank, self).move(i, j)
            if fun:
                fun()
            self.owner.nextUnitAction()
        else:
            print 'Tanks can\'t go there'
            self.tile.map.addAction(self.move)
        
