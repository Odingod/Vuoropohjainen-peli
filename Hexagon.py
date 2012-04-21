# -*- coding: utf-8 -*-
'''
Created on Jul 25, 2011

@author: anttir
'''
from math import sqrt
from PySide.QtGui import QMenu, QGraphicsPolygonItem, QPolygon, QBrush, QPen, QPixmap, QGraphicsPixmapItem, QImage, QPainter, QPen
from PySide.QtCore import QRect, QPoint, Qt
from functools import partial
from Terrains import *
from Units import Unit
from Players import Player
from save import saveable, load
import heapq

showUnitDialog = None
mapSize = 1

class Hexagon(object):
    neighbor_di = (0, 1, 1, 0, -1, -1)
    neighbor_dj = ((-1, -1, 0, 1, 0, -1), (-1, 0, 1, 1, 1, 0))
    def __init__(self, i, j, radius=20, loading=False):
        if loading:
            return

        self.i = i
        self.j = j
        self.r = radius
        self.w = 2 * self.r
        self.s = 3 * self.r / 2
        self.h = sqrt(3) * self.r
        self.x = i * self.s
        self.y = j * self.h + i % 2 * self.h / 2
        self.corners = ((self.r / 2, 0), (self.s, 0), (self.w, self.h / 2), (self.s, self.h), (self.r / 2, self.h), (0, self.h / 2))
        self.corners = [(a + self.x, b + self.y) for a, b in self.corners]
        self.chosen = False
        
    def __saveable__(self):
        d = {}

        d['i'] = self.i
        d['j'] = self.j
        d['r'] = self.r
        d['w'] = self.w
        d['s'] = self.s
        d['h'] = self.h
        d['x'] = self.x
        d['y'] = self.y
        d['corners'] = self.corners

        return d

    @classmethod
    def __load__(cls, d, h=None):
        if not h:
            h = cls(0, 0, loading=True)

        h.i = d['i']
        h.j = d['j']
        h.r = d['r']
        h.w = d['w']
        h.s = d['s']
        h.h = d['h']
        h.x = d['x']
        h.y = d['y']
        h.corners = d['corners']
        h.chosen = False

        return h
        
    def getNeighborI(self, number):
        i, j = self.i + Hexagon.neighbor_di[number], self.j + Hexagon.neighbor_dj[self.i % 2][number]
        if i >= 0 and j >= 0:
            return (i, j)
        return None
    
    def getNeighborsI(self):
        return [self.getNeighborI(i) for i in xrange(6)]
    
    def getBoardNeighbors(self):
        # Returns only neighbors who are in board
        temp = []
        for x in self.getNeighborsI():
            if x and x[0] >= 0 and x[1] >= 0 and x[0] < len(self.map.tiles) and x[1] < len(self.map.tiles[0]):
                temp.append(x)
        return temp
        
    def getImageRect(self):
        return QRect((QPoint(*self.corners[0]) + QPoint(*self.corners[5])) / 2, (QPoint(*self.corners[2]) + QPoint(*self.corners[3])) / 2)
        
        
class Tile(Hexagon, QGraphicsPolygonItem):
    def __init__(self, i, j, r, map, terrain=Ground(), loading=False):
        if loading:
            return

        Hexagon.__init__(self, i, j, r, loading=loading)
        poly = QPolygon()
        for p in self.corners:
            poly << QPoint(*p)
        QGraphicsPolygonItem.__init__(self, poly)
        self.terrain = terrain
        self.units = []
        self.unitImages = []
        self.map = map
        self.setBrush(QBrush(self.terrain.image))
        self.setPen(QPen())

    def __saveable__(self):
        d = Hexagon.__saveable__(self)

        d['terrain'] = saveable(self.terrain)
        d['units'] = map(saveable, self.units)
        # No need to save unitImages, can be loaded from self.units.
        
        return d

    @classmethod
    def __load__(cls, d, game):
        t = cls(0, 0, 0, None, loading=True)
        Hexagon.__load__(d, t)

        t.map = game.map
        t.terrain = load(Terrain, d['terrain'])
        t.units = []
        t.unitImages = []
        units = map(partial(load, Unit, game=game, tile=t), d['units'])
        
        poly = QPolygon()
        for p in t.corners:
            poly << QPoint(*p)
        QGraphicsPolygonItem.__init__(t, poly)

        t.setBrush(QBrush(t.terrain.image))
        t.setPen(QPen())

        for unit in units:
            t.addUnit(unit)

        return t
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.map.waitingInput:
                self.map.tellClick(self.i, self.j)
            elif self.units:
                showUnitDialog(self.units, event)
            self.scene().update()
        if event.button() == Qt.RightButton:
            self.getContextMenu().exec_(event.screenPos())
            self.ungrabMouse()
    
    def getContextMenu(self):       
        menu = QMenu()
        menu.addAction('Dist').triggered.connect(self.distAction)
        menu.addAction('Info').triggered.connect(self.info)
        return menu
    
    def info(self):
        if isinstance(self.terrain, Ground):
            info = 'Some dirt'
        elif isinstance(self.terrain, Water):
            info = 'There is some sparkling water'
        if self.units:
            info += ' and a tank with ' + str(self.units[0].hp) + ' health.'
        print info
    
    def distAction(self):
        self.map.addAction(partial(self.distance, out=True))
        
    def distance(self, i, j, out=False):
        di = i - self.i
        dj = j - self.j
        dist = 0
        if dj == 0 or di == 0:
            dist = max(abs(dj), abs(di))
            if out:
                print 'dist: ' + str(dist)
            return dist
        startj, starti = max((j, i), (self.j, self.i))
        endj, endi = min((j, i), (self.j, self.i))
        if starti > endi:
            while starti > endi:
                dist += 1
                starti -= 1
                startj -= starti % 2
            while startj > endj:
                dist += 1
                startj -= 1
        else:
            while starti < endi:
                dist += 1
                starti += 1
                startj -= starti % 2
            while startj > endj:
                dist += 1
                startj -= 1
        if out:
            print 'dist: ' + str(dist)
        return dist

    def canReach(self, i, j, dist, getReachables=False):
        # Säilytetään juttuja leveyshakua varten
        lista = [(0, 0, self)]

        # Säilytetään jo käydyt jutut ettei käydä uusiksi
        used = set([])
        reachables = set([])

        while lista:
            curdist, length, current = heapq.heappop(lista)
            used.add(current)

            if (length > dist) or (not current.terrain.canHoldUnit) or \
                    (curdist > dist - length and not getReachables) or \
                    ((current.i != i or current.j != j) and current.units):
                continue

            reachables.add(current)

            if current.i == i and current.j == j and not getReachables:
                return len(current.units) == 0

            for x in current.getBoardNeighbors():
                tile = self.map.tiles[x[0]][x[1]]
                if not tile in used:
                    heapq.heappush(lista, (tile.distance(i, j), length+1, tile))

        if getReachables:
            # Filter out the ones that have units in them.
            return filter(lambda x: not x.units, reachables)

        return False
                
    def setChosen(self, ch):
        self.chosen = ch
        if ch:
            redPen = QPen(Qt.red)
            redPen.setWidth(2)
            self.setPen(redPen)
        else:
            self.setPen(QPen())

    def setChosenWithNeighbours(self):
        self.setChosenByDist(1)
    
    def setChosenByDist(self, dist):
        if not (isinstance(dist, tuple) or isinstance(dist, list)):
            dist = (dist,)

        for row in self.map.tiles:
            for hex in row:
                if hex.distance(self.i, self.j) in dist:
                    hex.setChosen(True)
                else:
                    hex.setChosen(False)
    
    def setChosenByReach(self, reach):
        if isinstance(reach, tuple) or isinstance(reach, list):
            if reach:
                reach = max(reach)
            else:
                reach = -1

        # Deselect all
        self.setChosenByDist(-1)

        for reachable in self.canReach(self.i, self.j, reach, True):
            reachable.setChosen(True)
    
    def addUnit(self, unit):
        global mapSize
        unit.tile = self
        self.units.append(unit)
        img = QImage(unit.image).scaledToWidth(self.getImageRect().width())
        if unit.owner:
            rect = img.rect()
            painter = QPainter(img)
            painter.setPen(unit.owner.unitColor())
            painter.drawEllipse(rect)

            hpWidth = 20
            greenWidth = unit.hp / float(unit.maxHp) * hpWidth
            painter.fillRect(5, 5, greenWidth, 5, Qt.green)
            painter.fillRect(5 + greenWidth, 5, hpWidth-greenWidth, 5, Qt.red)
            painter.end()
        image = QGraphicsPixmapItem(QPixmap(img), self)
        image.setOffset(self.x + 12/(2*mapSize), self.y + 10/(2*mapSize))
        self.unitImages.append(image)
    
    def getUnit(self):
        return self.units
    def canBuild(self):
        for i in range(len(self.units)):
            if self.units[i].getId() == "tank":
                return False
        return True
    
    def removeUnit(self, unit):
        try:
            i = self.units.index(unit)
            self.units.pop(i)
            self.unitImages[i].setParentItem(None)
            self.unitImages.pop(i)
        except ValueError:
            pass
