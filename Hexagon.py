'''
Created on Jul 25, 2011

@author: anttir
'''
from math import sqrt,floor, copysign
from PySide.QtGui import QImage,QMenu
from PySide.QtCore import QRect,QPoint
from random import randint
from functools import partial

class Hexagon():
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
        



class Map():
    def __init__(self):
        self.tiles=[[]]
        self.metrics=Hexagon(-1,-1)
        self.waitingInput=[]
    
    def createSquareMap(self,w=10,h=10,r=20):
        self.metrics=Hexagon(-1,-1,r)
        for i in xrange(w):
            self.tiles.append([])
            for j in xrange(h):
                self.tiles[i].append(Tile(i,j,r,self,Ground() if randint(1,10)<-1 else Water()))
        self.tiles[2][3].addUnit(Tank())
    
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
        self.image=image
        
class Ground(Terrain):
    def __init__(self):
        Terrain.__init__(self, 'ground', QImage('earth.png'))
        
class Water(Terrain):
    def __init__(self):
        Terrain.__init__(self, 'water', QImage('water.png'))

class Tile(Hexagon):
    def __init__(self,i,j,r,map,terrain=Ground()):
        Hexagon.__init__(self, i, j, r)
        self.terrain=terrain
        self.units=[]
        self.map=map
    
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
        di=i-self.i
        dj=j-self.j
        if copysign(1,di) == copysign(1,dj):
            dist = max(abs(di),abs(dj));
        else:
            dist = abs(di) + abs(dj);
        print 'Distance is '+str(dist)
        

    
    def addUnit(self,unit):
        unit.tile=self
        self.units.append(unit)
    
    def removeUnit(self,unit):
        try:
            self.units.remove(unit)
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
        tiles[i][j].units.append(self)
        self.tile=tiles[i][j]
        
class Tank(Unit):
    def __init__(self,tile=None):
        Unit.__init__(self, 'tank', QImage('alien1.gif'), tile)
    
    def move(self,i,j):
        if self.tile.map.tiles[i][j].terrain.id == 'water':
            print 'Tanks can\'t swim'
        else:
            super(Tank,self).move(i,j)
        
