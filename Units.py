from PySide.QtGui import QImage
from PySide.QtCore import QCoreApplication
from save import saveable, load
from Players import Player
from functools import partial

class Unit(object):
    def __init__(self, id, image, tile=None, moves=(0, 1), hp=30, damage=10, range=(1,), owner=None):
        self.id = id
        self.image = image
        self.tile = tile
        self.moves = moves
        self.hp = hp
        self.maxHp = hp
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

    def move_to(self, i, j):
        tiles = self.tile.map.tiles
        self.tile.removeUnit(self)
        tiles[i][j].addUnit(self)
        self.tile.setChosenByDist(-1)
        self.tile.ensureVisible()
        QCoreApplication.instance().processEvents()

    def move(self, i, j, fun=None, ai=False):
        if not self.tile.map.tiles[i][j].chosen and not ai:
            print "You can't move there"
            self.tile.setChosenByDist(0)
        elif self.tile.map.tiles[i][j].terrain.canHoldUnit:
            self.move_to(i, j)
            self.owner.unitDone()

            if fun:
                fun()
        else:
            print 'This unit can\'t go there'
            self.tile.map.addAction(self.move)
    
    def unitDialog(self):
        showUnitDialog(self)

    def build(self, *args):
        print 'This unit cannot build!'

    def recruit(self, *args):
        print 'This unit cannot recruit!'

    def isInRange(self, other):
        return self.tile.distance(other.tile.i, other.tile.j) in self.range

    def attack(self, other):
        if not self.isInRange(other):
            print 'That unit is out of your range.'
            return False

        return other.takeDamage(self.damage)

    def attackTile(self, i, j, fun=None):
        units = self.tile.map.tiles[i][j].units

        if units:
            if self.attack(units[0]):
                self.tile.setChosenByDist(-1)
                self.owner.unitDone()

                if fun:
                    fun()

                return True
        else:
            print 'There is no unit in there'

        self.tile.setChosenByDist(0)
        return False

    def takeDamage(self, amount):
        amount = min(amount, self.hp)
        self.hp -= amount

        if self.hp == 0:
            self.remove()
        else:
            print '{0} took {1} damage!'.format(self.id, amount)
            # Redraw the hp bar
            self.tile.removeUnit(self)
            self.tile.addUnit(self)

        return True

    def remove(self):
        print '{0} died!'.format(self.id)
        self.tile.removeUnit(self)
        self.owner.removeUnit(self)
        self.tile.map.units.remove(self)

class Building(Unit):
    def __init__(self, *args, **kwargs):
        kwargs.pop('moves', None)
        Unit.__init__(self, *args, moves=(), **kwargs)

    def move(self, i=None, j=None, ai=False):
        print "can't move a building"
		
class Tank(Unit):
    def __init__(self, tile=None, owner=None):
        Unit.__init__(self, 'tank', QImage('alien1.png'), tile, (1, 2, 3), 25, 20, (1,2), owner)
    
class Melee(Unit):
    def __init__(self, tile=None, owner=None):
        Unit.__init__(self, 'melee', QImage('melee.png'), tile, (1, 2, 3, 4), 20, 10, (1,), owner)

class Ranged(Unit):
    def __init__(self, tile=None, owner=None):
        Unit.__init__(self, 'ranged', QImage('ranged.png'), tile, (1, 2), 15, 15, (1, 2), owner)

class Builder(Unit):
    def __init__(self, tile=None, owner=None):
        moves = (1, 2, 3)
        hp = 10
        damage = 0
        range = ()
        Unit.__init__(self, 'builder', QImage('builder.png'), tile=tile,
                owner=owner, moves=moves, hp=hp, damage=damage, range=range)
        from Settlement import *
        self.buildings = {
            'settlement': Settlement,
        }
        self.buildRange = (1,)
        self.building = None

    def build(self, building):
        if building in self.buildings:
            self.building = building
            self.tile.map.addAction(self.doBuild)
            self.tile.setChosenByReach(self.buildRange)
        else:
            print 'Cannot build such unit.'
            return False

        return True

    def doBuild(self, i, j):
        if not self.build:
            print 'Nothing to build! Something is wrong.'
            self.tile.setChosenByDist(0)
            return False

        if not self.tile.map.tiles[i][j].chosen:
            print 'Cannot build there!'
            self.tile.setChosenByDist(0)
            return False
        
        self.tile.setChosenByDist(-1)
        tile = self.tile.map.tiles[i][j]
        u = self.buildings[self.building](tile=tile, owner=self.owner)
        self.building = None
        self.tile.map.units.append(u)
        tile.addUnit(u)
        self.owner.unitCount += 1
        self.owner.unitDone()
