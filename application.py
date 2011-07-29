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
            self.currentUnit = None
        else:
            self.currentUnit = self.map.units[self.unitIndex]
    
    def resetUnitCycle(self):
        self.unitIndex = -1

    def moveAction(self):
        self.map.addAction(self.currentUnit.move)

    def distAction(self):
        self.map.addAction(self.currentUnit.tile.distance)

    def nextUnitAction(self, *args):
        self.cycleUnits()
        if self.currentUnit:
            self.currentUnit.tile.setChosenWithNeighbours()
            self.currentUnit.tile.ensureVisible()
        else:
            self.nextTurnAction()

    def nextTurnAction(self):
        self.resetUnitCycle()
        self.nextUnitAction()

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
    def __init__(self, parent):
        super(NewGameDialog, self).__init__(parent)
        layout = QFormLayout()
        self.numUnits = QSpinBox()
        self.numUnits.setRange(1, 15)
        self.numUnits.setValue(5)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | \
            QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addRow(self.numUnits)
        layout.addRow(buttons)
        self.setLayout(layout)

    def accept(self):
        game.numUnits = self.numUnits.value()
        super(NewGameDialog, self).accept()

class BottomDock(QDockWidget):
    def __init__(self, parent):
        super(BottomDock, self).__init__(parent)

        layout = QFormLayout()
        self.moveButton = QPushButton("Move")
        self.distButton = QPushButton("Dist")
        self.nextUnitButton = QPushButton("Next Unit")
        self.nextTurnButton= QPushButton("Next Turn")
        self.moveButton.clicked.connect(self.moveAction)
        self.distButton.clicked.connect(self.distAction)
        self.nextUnitButton.clicked.connect(self.nextUnitAction)
        self.nextTurnButton.clicked.connect(self.nextTurnAction)

        actionButtonGroupBox = QGroupBox()
        abLayout = QHBoxLayout()
        abLayout.addWidget(self.moveButton)
        abLayout.addWidget(self.distButton)
        actionButtonGroupBox.setLayout(abLayout)

        turnControlButtonGroupBox = QGroupBox()
        tcLayout = QHBoxLayout()
        tcLayout.addWidget(self.nextUnitButton)
        tcLayout.addWidget(self.nextTurnButton)
        turnControlButtonGroupBox.setLayout(tcLayout)

        layout.addRow("Select Action", actionButtonGroupBox)
        layout.addRow(turnControlButtonGroupBox)
        bottomDockWidget = QWidget()
        bottomDockWidget.setLayout(layout)
        self.setWidget(bottomDockWidget)

    def moveAction(self):
        game.moveAction()
        self.disableButtons()

    def distAction(self):
        game.distAction()
        self.disableButtons()

    def nextUnitAction(self):
        game.nextUnitAction()
        self.enableButtons()

    def nextTurnAction(self):
        game.nextTurnAction()
        self.enableButtons()

    def disableButtons(self):
        self.moveButton.setEnabled(False)
        self.distButton.setEnabled(False)

    def enableButtons(self):
        self.moveButton.setEnabled(True)
        self.distButton.setEnabled(True)
                
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
        self.bottomDock = BottomDock(self)
        self.bottomDock.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.bottomDock)

    def newGame(self):
        global game
        self.mainScene = QGraphicsScene()
        self.mainView = MainView(self.mainScene)
        game = Game()
        newGameDialog = NewGameDialog(self)
        r = newGameDialog.exec_()

        if r == QDialog.Rejected:
            self.close()

        game.start()
        [[self.mainScene.addItem(hex) for hex in row] for row in game.map.tiles]

        self.setCentralWidget(self.mainView)
        self.mainView.show()
        game.nextUnitAction()

if __name__ == "__main__":
    app = QApplication([])

    window = MainWindow()
    window.setWindowTitle("Super peli!")
    window.show()

    app.exec_()
