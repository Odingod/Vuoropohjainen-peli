#!/usr/bin/env python
from PySide.QtCore import *
from PySide.QtGui import *
from Hexagon import Hexagon, Map

class Game:
    def __init__(self):
        self.map=Map()
        self.map.createSquareMap(10,10,50)

class MainView(QGraphicsView):
    def __init__(self, scene):
        super(MainView, self).__init__(scene)

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.buildMenu()
        self.newGame()

    def buildMenu(self):
        # Game menu actions
        quitAct = QAction("&Quit", self)
        quitAct.setShortcuts(QKeySequence.Quit)
        quitAct.triggered.connect(self.close)
        newGameAct = QAction("&New Game", self)
        newGameAct.setShortcuts(QKeySequence.New)
        newGameAct.triggered.connect(self.newGame)

        # Create Game menu
        gameMenu = self.menuBar().addMenu("&Game")
        gameMenu.addAction(newGameAct)
        gameMenu.addAction(quitAct)

    def newGame(self):
        self.mainScene = QGraphicsScene()
        self.mainView = MainView(self.mainScene)
        self.game = Game()

        [[self.mainScene.addItem(hex) for hex in row] for row in self.game.map.tiles]

        self.setCentralWidget(self.mainView)
        self.mainView.show()

if __name__ == "__main__":
    app = QApplication([])

    window = MainWindow()
    window.setWindowTitle("Super peli!")
    window.show()

    app.exec_()
