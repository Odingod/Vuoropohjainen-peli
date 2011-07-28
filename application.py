#!/usr/bin/env python
from PySide.QtCore import *
from PySide.QtGui import *
from Hexagon import Hexagon, Map

class Game:
    def __init__(self):
        self.map=Map()
        self.numUnits = 1

    def start(self):
        self.map.createSquareMap(self.numUnits, 10,10,50)

class MainView(QGraphicsView):
    def __init__(self, scene):
        super(MainView, self).__init__(scene)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragPos = event.globalPos()
            self.dragPossible = True
            self.dragging = False
        super(MainView, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setCursor(Qt.ArrowCursor)
            self.dragPossible = False
            self.dragging = False
        super(MainView, self).mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        if self.dragPossible:
            self.setCursor(Qt.ClosedHandCursor)
            if self.dragging:
                dx, dy = (self.dragPos - event.globalPos()).toTuple()
                self.dragPos = event.globalPos()
                self.verticalScrollBar().setValue(self.verticalScrollBar().value() + dy)
                self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() + dx)
                self.verticalScrollBar().triggerAction(QAbstractSlider.SliderMove)
                self.horizontalScrollBar().triggerAction(QAbstractSlider.SliderMove)
            elif (self.dragPos - event.globalPos()).manhattanLength() < QApplication.startDragDistance():
                self.dragging = True

class NewGameDialog(QDialog):
    def __init__(self, game, parent):
        super(NewGameDialog, self).__init__(parent)
        self.game = game
        layout = QFormLayout()
        self.numUnits = QSpinBox()
        self.numUnits.setRange(1, 15)
        self.numUnits.setValue(1)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | \
            QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addRow("Number Of Units", self.numUnits)
        layout.addRow(buttons)
        self.setLayout(layout)

    def accept(self):
        self.game.numUnits = self.numUnits.value()
        super(NewGameDialog, self).accept()
                
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
        newGameDialog = NewGameDialog(self.game, self)
        r = newGameDialog.exec_()

        if r == QDialog.Rejected:
            self.close()

        self.game.start()
        [[self.mainScene.addItem(hex) for hex in row] for row in self.game.map.tiles]

        self.setCentralWidget(self.mainView)
        self.mainView.show()
        self.mainView.centerOn(self.mainScene.sceneRect().center())

if __name__ == "__main__":
    app = QApplication([])

    window = MainWindow()
    window.setWindowTitle("Super peli!")
    window.show()

    app.exec_()
