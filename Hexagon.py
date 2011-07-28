'''
Created on Jul 25, 2011

@author: anttir
'''
from math import sqrt,floor, copysign
from PySide.QtGui import QImage, QMenu, QGraphicsPolygonItem, QPolygon, QBrush, QPen, QPixmap, QGraphicsPixmapItem
from PySide.QtCore import QRect, QPoint, Qt
from random import randint, choice
from functools import partial

class Hexagon(object):
    neighbor_di=(0, 1, 1, 0, -1, -1)
    neighbor_dj=((-1, -1, 0, 1, 0, -1),(-1, 0, 1, 1, 1, 0 ))
    def __init__(self,i,j,radius=20):
        self.i=i
        self.j=j
        self.r=radius
        self.w=2*self.r
        self.s=3*self.r/2
        self.h=sqrt(3)*self.r
        self.x=i*self.s
        self.y=j*self.h+i%2*self.h/2
        self.corners= ((self.r/2,0),(self.s,0),(self.w,self.h/2),(self.s,self.h),(self.r/2,self.h),(0,self.h/2))
        self.corners= [(a+self.x,b+self.y) for a,b in self.corners]
        self.chosen=False
        
        
    def getNeighborI(self,number):
        i,j=self.i+Hexagon.neighbor_di[number],self.j+Hexagon.neighbor_dj[self.i%2][number]
        if i >= 0 and j >= 0:
            return (i,j)
        return None
    
    def getNeighborsI(self):
        return [self.getNeighborI(i) for i in xrange(6)]
    
    def getImageRect(self):
        return QRect((QPoint(*self.corners[0])+QPoint(*self.corners[5]))/2,(QPoint(*self.corners[2])+QPoint(*self.corners[3]))/2)
        



class Map(object):
    def __init__(self):
        self.tiles=[]
        self.metrics=Hexagon(-1,-1)
        self.waitingInput=[]
    
    def createSquareMap(self, numUnits, w=10,h=10,r=20):
        self.metrics=Hexagon(-1,-1,r)
        for i in xrange(w):
            self.tiles.append([])
            for j in xrange(h):
                self.tiles[i].append(Tile(i,j,r,self,Ground() if randint(1,10)< 10 else Water()))
        for i in xrange(numUnits):
            while True:
                #tile = choice(choice(self.tiles))
                row = choice(self.tiles)
                tile = choice(row)
                if tile.terrain.canHoldUnit and not tile.units:
                    tile.addUnit(Tank())
                    break
    
    def getHexAt(self,x,y):
        i_t=x/self.metrics.s
        j_t=int(floor((y-(i_t%2)*self.metrics.h/2)/self.metrics.h))
        x_t=x-i_t*self.metrics.s
        y_t=(y-(i_t%2)*self.metrics.h/2)-j_t*self.metrics.h
        d_j=1 if y_t>self.metrics.h/2 else 0
        if x_t >self.metrics.r*abs(1./2.-y_t/self.metrics.h):
            return (i_t,j_t)
        else:
            return (i_t-1,j_t-(i_t-1)%2+d_j)
    
    def tellClick(self,i,j):
        if self.waitingInput:
            for action in self.waitingInput:
                action(i,j)
                self.waitingInput.remove(action)
    
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

class Tile(Hexagon, QGraphicsPolygonItem):
    def __init__(self,i,j,r,map,terrain=Ground()):
        Hexagon.__init__(self, i, j, r)
        poly = QPolygon()
        for p in self.corners:
            poly << QPoint(*p)
        QGraphicsPolygonItem.__init__(self, poly)
        self.terrain=terrain
        self.units=[]
        self.unitImages = []
        self.map=map
        self.setBrush(QBrush(self.terrain.image))
        self.setPen(QPen())
    
    def mousePressEvent(self, event):
        neighbours = []
        for n in self.getNeighborsI():
            if n:
                try:
                    neighbours.append(self.map.tiles[n[0]][n[1]])
                except IndexError:
                    pass

        for row in self.map.tiles:
            for n in row:
                if n in neighbours:
                    n.setChosen(True)
                else:
                    n.setChosen(False)
        self.setChosen(True)

        if event.button() == Qt.RightButton:
            menu = self.getContextMenu()
            menu.exec_(event.screenPos())
            self.ungrabMouse()
        elif event.button() == Qt.LeftButton:
            self.map.tellClick(self.i, self.j)

        self.scene().update()
        
    def getContextMenu(self):
        menu = QMenu()
        if self.units:
            menu.addAction('Move').triggered.connect(self.moveAction)
        
        menu.addAction('Dist').triggered.connect(self.distA)
        menu.addAction('Cancel')
        return menu

    def distA(self):
        self.map.waitingInput.append(self.distance)
        
    def moveAction(self):
        self.map.waitingInput.append(self.moveUnit)
    
    def moveUnit(self,i,j):
        self.units[0].move(i,j)
    
    def distance(self,i,j):
        di=-(i-self.i)
        dj=j-self.j
        dist = abs(di) + abs(dj) - abs(di)%2;
        print 'Distance is '+str(dist)
        
    def setChosen(self, ch):
        self.chosen = ch
        if ch:
            redPen = QPen(Qt.red)
            redPen.setWidth(2)
            self.setPen(redPen)
        else:
            self.setPen(QPen())

    
    def addUnit(self,unit):
        unit.tile=self
        self.units.append(unit)
        image = QGraphicsPixmapItem(QPixmap(unit.image), self)
        image.setOffset(self.x + 12, self.y + 10)
        self.unitImages.append(image)
    
    def removeUnit(self,unit):
        try:
            i = self.units.index(unit)
            self.units.pop(i)
            self.unitImages[i].setParentItem(None)
            self.unitImages.pop(i)
        except ValueError:
            pass
        
class Unit(object):
    def __init__(self,id,image,tile=None):
        self.id=id
        self.image=image
        self.tile=tile
    
    def move(self,i,j):
        tiles=self.tile.map.tiles
        self.tile.removeUnit(self)
        tiles[i][j].addUnit(self)
        
class Tank(Unit):
    def __init__(self,tile=None):
        Unit.__init__(self, 'tank', QImage('alien1.gif'), tile)
    
    def move(self,i,j):
        if self.tile.map.tiles[i][j].terrain.canHoldUnit:
            super(Tank,self).move(i,j)
        else:
            print 'Tanks can\'t go there'
        
