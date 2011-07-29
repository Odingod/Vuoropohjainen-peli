#!/usr/bin/env python
from PySide.QtCore import *
from PySide.QtGui import *
from Hexagon import Hexagon, Map

class Game:
    def __init__(self):
        self.map=Map()
        self.numUnits = 1
        self.unitIndex = -1 

    def start(self):
        self.map.createSquareMap(self.numUnits, 10,10,50)

    def cycleUnits(self):
        self.unitIndex += 1
        if self.unitIndex == self.numUnits:
            self.unitIndex = -1 
            return None
        else:
            return self.map.units[self.unitIndex]
    
    def resetUnitCycle(self):
        self.unitIndex = -1

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
        self.numUnits.setValue(5)
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
        self.newGame()
        self.buildMenu()
        self.buildBottomDock()

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

    def buildBottomDock(self):
        self.bottomDock = QDockWidget(self)
        self.bottomDock.setFeatures(QDockWidget.NoDockWidgetFeatures)
        layout = QFormLayout()
        moveButton = QPushButton("Move")
        distButton = QPushButton("Dist")
        nextUnitButton = QPushButton("Next Unit")
        nextTurnButton= QPushButton("Next Turn")
        moveButton.clicked.connect(self.moveAction)
        distButton.clicked.connect(self.distAction)
        nextUnitButton.clicked.connect(self.nextUnitAction)
        nextTurnButton.clicked.connect(self.nextTurnAction)

        actionButtonGroupBox = QGroupBox()
        abLayout = QHBoxLayout()
        abLayout.addWidget(moveButton)
        abLayout.addWidget(distButton)
        actionButtonGroupBox.setLayout(abLayout)

        turnControlButtonGroupBox = QGroupBox()
        tcLayout = QHBoxLayout()
        tcLayout.addWidget(nextUnitButton)
        tcLayout.addWidget(nextTurnButton)
        turnControlButtonGroupBox.setLayout(tcLayout)

        layout.addRow("Select Action", actionButtonGroupBox)
        layout.addRow(turnControlButtonGroupBox)
        bottomDockWidget = QWidget()
        bottomDockWidget.setLayout(layout)
        self.bottomDock.setWidget(bottomDockWidget)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.bottomDock)

    def moveAction(self):
        self.game.map.addAction(self.currentUnit.move)
        self.game.map.addAction(self.nextUnitAction)

    def distAction(self):
        self.game.map.addAction(self.currentUnit.tile.distance)
        self.game.map.addAction(self.nextUnitAction)

    def nextUnitAction(self, *args):
        self.currentUnit = self.game.cycleUnits()
        if self.currentUnit:
            self.currentUnit.tile.setChosenWithNeighbours()
            self.mainView.ensureVisible(self.currentUnit.tile)
        else:
            self.nextTurnAction()


    def nextTurnAction(self):
        self.game.resetUnitCycle()
        self.nextUnitAction()

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
        self.nextUnitAction()

if __name__ == "__main__":
    app = QApplication([])

    window = MainWindow()
    window.setWindowTitle("Super peli!")
    window.show()

    app.exec_()
