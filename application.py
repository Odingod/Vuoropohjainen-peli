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
from Players import Player, HumanPlayer, AIPlayer
from functools import partial
import sys
from save import saveable, load
import json

class Game:
    def __init__(self):
        self.map = Map()
        self.numUnits = 1
        self.numPlayers = 1
        self.playerIndex = -1 
        self.turn = 1
        self.players = []

    def __saveable__(self):
        """ Returns a saveable representation of the game. """
        d = {}

        d['players'] = map(saveable, self.players)
        d['map'] = saveable(self.map)
        d['turn'] = self.turn
        d['playerIndex'] = self.playerIndex
        d['currentPlayer'] = saveable(self.currentPlayer)

        return d

    @classmethod
    def __load__(cls, d):
        g = cls()

        g.map = load(Map, d['map'], game=g)
        g.players = map(partial(load, Player, game=g), d['players'])
        g.turn = d['turn']
        g.playerIndex = d['playerIndex']
        g.currentPlayer = load(Player, d['currentPlayer'], game=g)
        g.numUnits = len(g.map.units)
        g.numPlayers = len(g.players)

        return g

    def save(self, filename):
        d = saveable(self)

        with open(filename, 'w') as f:
            json.dump(d, f)

        print 'Game saved.'

    @classmethod
    def load(cls, filename):
        Player.loadedPlayers = {}

        with open(filename) as f:
            d = json.load(f)

        print 'Game loaded.'
        return load(cls, d)

    def start(self):
        self.players.append(HumanPlayer(self))
        for x in xrange(self.numPlayers - 1):
            self.players.append(AIPlayer(self))
        self.map.createSquareMap(self.numUnits, self.players, 10, 10, 50)
        self.numUnits *= self.numPlayers
        
    def cyclePlayers(self):
        self.playerIndex += 1
        if self.playerIndex == self.numPlayers:
            self.playerIndex = -1 
            self.currentPlayer = None # None indicates the turn is over
        else:
            self.currentPlayer = self.players[self.playerIndex]
    
    def nextPlayerAction(self):
        self.cyclePlayers()
        if self.currentPlayer:
            self.currentPlayer.doTurn()
        else:
            self.nextTurn()
    
    def nextTurn(self):
        self.save('savefile.save')
        self.resetPlayerCycle()
        self.nextPlayerAction()
        self.turn += 1
    
    def resetPlayerCycle(self):
        self.playerIndex = -1
    
    def moveAction(self, fun):
        if isinstance(self.currentPlayer, HumanPlayer):
            if not self.currentPlayer.currentUnit.moves:
                print 'This unit cannot move!'
                return False

            self.currentPlayer.currentUnit.tile.setChosenByReach(
                    self.currentPlayer.currentUnit.moves)
            self.map.addAction(partial(
                self.currentPlayer.currentUnit.move, fun=fun))
            return True
        return False

    def attackAction(self, fun):
        if isinstance(self.currentPlayer, HumanPlayer):
            unit = self.currentPlayer.currentUnit
            unit.tile.setChosenByDist(unit.range)
            self.map.addAction(partial(unit.attackTile, fun=fun))
            return True
        return False

    def buildAction(self, building):
        if isinstance(self.currentPlayer, HumanPlayer):
            return self.currentPlayer.currentUnit.build(building)
        return False

    def recruitAction(self, unit):
        if isinstance(self.currentPlayer, HumanPlayer):
            return self.currentPlayer.currentUnit.recruit(unit)
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
        self.distButton = QPushButton("Pass")
        self.nextUnitButton = QPushButton("Next Unit")
        self.nextTurnButton = QPushButton("Next Turn")
        self.moveButton = QPushButton("Move")
        self.attackButton = QPushButton("Attack")

        self.moveButton.clicked.connect(self.moveAction)
        self.nextUnitButton.clicked.connect(self.nextUnitAction)
        self.nextTurnButton.clicked.connect(self.nextTurnAction)
        self.attackButton.clicked.connect(self.attackAction)

        actionButtonGroupBox = QWidget()
        abLayout = QHBoxLayout()
        mar = abLayout.contentsMargins().bottom()
        abLayout.setContentsMargins(mar, mar, mar, 0)
        abLayout.addWidget(self.moveButton)
        abLayout.addWidget(self.attackButton)

        self.build_farmButton = QPushButton("Build farm")
        self.build_tankButton = QPushButton("Build tank")
        self.build_wallButton = QPushButton("Build wall")

        self.build_farmButton.clicked.connect(
                lambda: self.buildAction('farm'))
        self.build_wallButton.clicked.connect(
                lambda: self.buildAction('wall'))

        self.build_tankButton.clicked.connect(
                lambda: self.recruitAction('tank'))

        abLayout.addWidget(self.build_farmButton)
        abLayout.addWidget(self.build_tankButton)
        abLayout.addWidget(self.build_wallButton)
        actionButtonGroupBox.setLayout(abLayout)

        turnControlButtonGroupBox = QWidget()
        tcLayout = QHBoxLayout()
        tcLayout.setContentsMargins(mar, 0, mar, mar)
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

    def buildAction(self, building):
        if game.buildAction(building):
            self.nextUnitAction()

    def recruitAction(self, unit):
        if game.recruitAction(unit):
            self.nextUnitAction()

    def moveAction(self):
        game.moveAction(self.updateTitle)

    def attackAction(self):
        game.attackAction(self.nextUnitAction)

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

        try:
            game = Game.load('savefile.save')
        except Exception as e:
            print e
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

    # Have to do this manually here, after everything has been initialized,
    # because otherwise, the current unit might not be visible the first time
    # you start the game
    game.currentPlayer.currentUnit.tile.ensureVisible()

    app.exec_()
