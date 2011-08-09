#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
projekti-ideoita:
pienempiä
-kartan/pelin lataus/tallennus
-kartan generointi
-fog of war (karttaa pitää tutkia)
-lisää yksiköitä ja maastoja
-useampi taso karttaan (korkeuseroja)
-valikot riippuvat nykyisestä yksiköstä
-kartassa korkeuseroja
-pilvet, savu, ym. omassa tasossaan (scrollailee vähän eri tahtiin kuin maa, helppo 'melkein 3D' efekti)
-reitinhaku (A*)

suurempia

-tekee koko pelistä event pohjaisen
-taistelut (hankaluus riippuu miten totetutetaan, jos vain verrataan kahta lukua helppo, jos vaaditaan jotenkin pelaajan inputtia hankalampi)
-resursseja/niiden kerääjiä
-teknologiakehitys
-animaatiot (liikkuminen, räjähdykset, ym.)
-valikkojärjestelmän rankempi virittely

'''
from PySide.QtCore import *
from PySide.QtGui import *
from Map import Map
from Players import HumanPlayer, AIPlayer
from functools import partial
import sys

class Game:
    def __init__(self):
        self.map=Map()
        self.numUnits = 1
        self.numPlayers = 1
        self.playerIndex = -1 
        self.turn = 1
        self.players = []

    def start(self):
        self.players.append(HumanPlayer(self))
        for x in xrange(self.numPlayers-1):
            self.players.append(AIPlayer(self))
        self.map.createSquareMap(self.numUnits, self.players, 10,10,50)
        self.numUnits*=self.numPlayers
        
    def cyclePlayers(self):
        self.playerIndex += 1
        if self.playerIndex == self.numPlayers:
            self.playerIndex = -1 
            self.currentPlayer = None
        else:
            self.currentPlayer = self.players[self.playerIndex]
    
    
    
    def nextPlayerAction(self):
        self.cyclePlayers()
        if self.currentPlayer:
            self.currentPlayer.doTurn()
        else:
            self.nextTurn()
    
    def nextTurn(self):
        self.resetPlayerCycle()
        self.nextPlayerAction()
        self.turn += 1

    
    def resetPlayerCycle(self):
        self.playerIndex = -1
    
    def moveAction(self,fun):
        if isinstance(self.currentPlayer, HumanPlayer):
            self.currentPlayer.currentUnit.tile.setChosenByDist(self.currentPlayer.currentUnit.moves)
            self.map.addAction(partial(self.currentPlayer.currentUnit.move,fun=fun))
            return True
        return False
    
    def nextUnitAction(self):
        if isinstance(self.currentPlayer, HumanPlayer):
            self.currentPlayer.nextUnitAction()
            return True
        return False
    
    def nextTurnAction(self):
        if isinstance(self.currentPlayer, HumanPlayer):
            self.currentPlayer.endTurn()
            return True
        return False


    
        

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
            elif (self.dragPos - event.globalPos()).manhattanLength() > QApplication.startDragDistance():
                self.dragging = True

class NewGameDialog(QDialog):
    def __init__(self, parent):
        super(NewGameDialog, self).__init__(parent)
        layout = QFormLayout()
        self.numUnits = QSpinBox()
        self.numUnits.setRange(1, 15)
        self.numUnits.setValue(1)
        self.numPlayers = QSpinBox()
        self.numPlayers.setRange(1, 4)
        self.numPlayers.setValue(1)
        
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | \
            QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addRow("Number Of Units", self.numUnits)
        layout.addRow("Number Of Players", self.numPlayers)
        layout.addRow(buttons)
        self.setLayout(layout)

    def accept(self):
        game.numUnits = self.numUnits.value()
        game.numPlayers = self.numPlayers.value()
        super(NewGameDialog, self).accept()

class BottomDock(QDockWidget):
    def __init__(self, parent):
        super(BottomDock, self).__init__(parent)

        self.title = QLabel()
        self.title.setIndent(20)
        self.updateTitle()
        self.setTitleBarWidget(self.title)

        layout = QFormLayout()
        self.moveButton = QPushButton("Move")
        self.distButton = QPushButton("Pass")
        self.nextUnitButton = QPushButton("Next Unit")
        self.nextTurnButton= QPushButton("Next Turn")
        self.moveButton.clicked.connect(self.moveAction)
        self.distButton.clicked.connect(self.nextUnitAction)
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

        layout.addRow(actionButtonGroupBox)
        layout.addRow(turnControlButtonGroupBox)
        bottomDockWidget = QWidget()
        bottomDockWidget.setLayout(layout)
        self.setWidget(bottomDockWidget)

    def updateTitle(self):
        self.title.setText("Unit: %d   Turn: %d" % (game.currentPlayer.printableUnitIndex, game.turn))

    def moveAction(self):
        self.updateTitle()
        if game.moveAction(self.updateTitle):
            pass
            #self.disableButtons()

    def nextUnitAction(self):
        if game.nextUnitAction():
            self.updateTitle()
            self.enableButtons()

    def nextTurnAction(self):
        if game.nextTurnAction():
            self.updateTitle()
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

        if r == 0:
            self.close()
            sys.exit()

        game.start()
        [[self.mainScene.addItem(hex) for hex in row] for row in game.map.tiles]

        self.setCentralWidget(self.mainView)
        self.mainView.show()
        game.nextPlayerAction()

if __name__ == "__main__":
    app = QApplication([])

    window = MainWindow()
    window.setWindowTitle("Super peli!")
    window.show()

    # Have to do this manually here, after everything else has been
    # initialized and shown, or otherwise it won't work
    #game.currentUnit.tile.ensureVisible()
    # What's this^? works fine without it

    app.exec_()
