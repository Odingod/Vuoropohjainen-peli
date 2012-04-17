from PySide.QtGui import QImage
from PySide.QtCore import QCoreApplication
from save import saveable, load
from Players import Player

class Unit(object):
    def __init__(self, id, image, tile=None, moves=(0, 1), hp=30, damage=10, range=(1), owner=None):
        self.id = id
        self.image = image
        self.tile = tile
        self.moves = moves
        self.hp = hp
        self.damage = damage
        self.range = range
        self.owner = owner

    def __saveable__(self):
        d = {}

        d['id'] = self.id
        d['moves'] = self.moves
        d['hp'] = self.hp
        d['owner'] = saveable(self.owner)

        return d

    @classmethod
    def __load__(cls, d, game, tile):
        if d['id'] == 'tank':
            u = Tank()

        u.tile = tile
        u.moves = d['moves']
        u.hp = d['hp']
        u.owner = load(Player, d['owner'], game=game)

        return u
    def getId(self):
        return self.id
    def move(self, i, j):
        tiles = self.tile.map.tiles
        self.tile.removeUnit(self)
        tiles[i][j].addUnit(self)
        self.tile.setChosenByDist(-1)
        self.tile.ensureVisible()
        QCoreApplication.instance().processEvents()

    def build(self, *args):
        print 'This unit cannot build!'

    def recruit(self, *args):
        print 'This unit cannot recruit!'

class Building(Unit):
    def __init__(self, tile=None, owner=None):
        Unit.__init__(self, 'builting', QImage('castle_30x30.png'), tile, (0), 100, 0, (0), owner)

    def move(self, i=None, j=None, ai=False):
        print "can't move a building"
		
		
class Tank(Unit):
    def __init__(self, tile=None, owner=None):
        Unit.__init__(self, 'tank', QImage('alien1.png'), tile, (1, 2, 3), 25, 20, (1,2), owner)
    
    def move(self, i, j, fun=None, ai=False):
        if not self.tile.map.tiles[i][j].chosen and not ai:
            print "You can't move there"
            self.tile.map.addAction(self.move)
        elif self.tile.map.tiles[i][j].terrain.canHoldUnit:
            super(Tank, self).move(i, j)
            if fun:
                fun()

            if not ai:
                self.owner.nextUnitAction()
        else:
            print 'Tanks can\'t go there'
            self.tile.map.addAction(self.move)

class Melee(Unit):
    def __init__(self, tile=None, owner=None):
        Unit.__init__(self, 'melee', QImage('melee.png'), tile, (1, 2, 3, 4), 20, 10, (1), owner)
    
    def move(self, i, j, fun=None, ai=False):
        if not self.tile.map.tiles[i][j].chosen and not ai:
            print "You can't move there"
            self.tile.map.addAction(self.move)
        elif self.tile.map.tiles[i][j].terrain.canHoldUnit:
            super(Melee, self).move(i, j)
            if fun:
                fun()
            if not ai:
                self.owner.nextUnitAction()
        else:
            print 'Melee can\'t go there'
            self.tile.map.addAction(self.move)

class Ranged(Unit):
    def __init__(self, tile=None, owner=None):
        Unit.__init__(self, 'ranged', QImage('ranged.png'), tile, (1, 2), 15, 15, (1, 2), owner)
    
    def move(self, i, j, fun=None, ai=False):
        if not self.tile.map.tiles[i][j].chosen and not ai:
            print "You can't move there"
            self.tile.map.addAction(self.move)
        elif self.tile.map.tiles[i][j].terrain.canHoldUnit:
            super(Range, self).move(i, j)
            if fun:
                fun()
            if not ai:
                self.owner.nextUnitAction()
        else:
            print 'Ranged can\'t go there'
            self.tile.map.addAction(self.move)
