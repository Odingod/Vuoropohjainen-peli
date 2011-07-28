'''
Created on Jul 25, 2011

@author: anttir
'''
from PySide.QtCore import *
from PySide.QtGui import *
from Hexagon import Hexagon,Map
import sys

class HexaTest(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.map=Map()
        self.map.createSquareMap(10,10,50)
        self.i,self.j=-1,-1
    
    def paintEvent(self, paintevent):
        p=QPainter(self)
        normalPen=QPen()
        redPen=QPen(Qt.red)
        redPen.setWidth(2)
        save=[]
        for row in self.map.tiles:
            for hex in row:
                poly=QPolygon()
                p.setBrush((QBrush(hex.terrain.image)))
                p.setPen(normalPen)
                if hex.chosen:
                    p.setPen(redPen)
                for point in hex.corners:
                    poly << QPoint(*point)
                path=QPainterPath()
                path.addPolygon(poly)
                path.closeSubpath()
                p.drawPath(path)
                if hex.units:
                    for unit in hex.units:
                        p.drawImage(hex.getImageRect(),unit.image)
        if save:
            p.setPen(Qt.red)
            
            for hex in save:
                p.setBrush((QBrush(hex.terrain.image)))
                poly=QPolygon()
                for point in hex.corners:
                    poly << QPoint(*point)
                path=QPainterPath()
                path.addPolygon(poly)
                path.closeSubpath()
                
                p.drawPath(path)
            
    def mousePressEvent(self, event):
        try:
           self.map.tiles[self.i][self.j].setChosen(False)
           for neighbours in self.map.tiles[self.i][self.j].getNeighborsI():
               try:
                   self.map.tiles[neighbours[0]][neighbours[1]].setChosen(False)
               except (IndexError,TypeError):
                   pass
        except IndexError:
           pass
        
        self.i,self.j= self.map.getHexAt(event.x(), event.y())
        self.map.tiles[self.i][self.j].setChosen(True)
        for neighbours in self.map.tiles[self.i][self.j].getNeighborsI():
               try:
                   self.map.tiles[neighbours[0]][neighbours[1]].setChosen(True)
               except (IndexError,TypeError):
                   pass
        
        self.i,self.j= self.map.getHexAt(event.x(), event.y())
        print self.i , self.j
        if event.button() == Qt.RightButton:
            menu=self.map.tiles[self.i][self.j].getContextMenu()
            menu.exec_(event.globalPos())
        elif event.button() == Qt.LeftButton:
            self.map.tellClick(self.i,self.j)
            self.repaint()
        
        
if __name__=='__main__':
    app=QApplication(sys.argv)
    test=HexaTest()
    test.show()
    app.exec_()
    
