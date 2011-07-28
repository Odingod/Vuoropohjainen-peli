#!/usr/bin/env python
from PySide.QtCore import *
from PySide.QtGui import *
from Hexagon import Hexagon, Map

class MainView(QGraphicsView):
    def __init__(self, scene):
        super(MainView, self).__init__(scene)
        self.map=Map()
        self.map.createSquareMap(10,10,50)

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.mainScene = QGraphicsScene()
        self.mainView = MainView(self.mainScene)

        [[self.mainScene.addItem(hex) for hex in row] for row in self.mainView.map.tiles]

        self.setCentralWidget(self.mainView)

if __name__ == "__main__":
    app = QApplication([])

    window = MainWindow()
    window.setWindowTitle("Super peli!")
    window.mainView.show()
    window.show()

    app.exec_()
