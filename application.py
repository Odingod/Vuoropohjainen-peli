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
from Units import Unit
import Hexagon
from functools import partial
import sys
from save import saveable, load
import json

def _showUnitDialog(units, event):
    if game.singletonObject: return #only one pop up at a time
    for unit in units:
        if unit.owner == game.currentPlayer and unit not in unit.owner.doneUnits:
            game.currentPlayer.currentUnit = unit
            game.singletonObject = UnitActionForm(mainW)
            game.singletonObject.exec_()

class Game:
    def __init__(self):
        self.map = Map()
        self.numUnits = 1
        self.numPlayers = 1
        self.playerIndex = -1 
        self.turn = 1
        self.players = []
        self.mode = 'single'
        self.playerNames = []
        self.singletonObject = None
        self.turnUnits = []
        self.mapSize = 0 #small

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
        if game.mode == 'single':
            self.players.append(HumanPlayer(self))
            for x in xrange(self.numPlayers - 1):
                self.players.append(AIPlayer(self))
        else:
            for x in xrange(self.numPlayers):
                self.players.append(HumanPlayer(self))
        if self.mapSize == 0:
            self.map.createSquareMap(self.numUnits, self.players, 10, 10, 50)
        elif self.mapSize == 1:
            self.map.createSquareMap(self.numUnits, self.players, 20, 20, 35)
        else:
            self.map.createSquareMap(self.numUnits, self.players, 30, 30, 20)
        self.numUnits *= self.numPlayers
        
    def cyclePlayers(self):
        self.playerIndex += 1
        if self.playerIndex == self.numPlayers:
            self.playerIndex = -1 
            self.currentPlayer = None # None indicates the turn is over
        else:
            self.currentPlayer = self.players[self.playerIndex]
            if isinstance(self.currentPlayer, HumanPlayer):
                self.turnUnits = filter(lambda x: x.owner == self.currentPlayer, self.map.units)

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

    def attackAction(self, fun=None):
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

class PlayerNames(QDialog):
    def __init__(self, parent):
        super(PlayerNames, self).__init__(parent)
        layout = QFormLayout()
        self.texts = []
        
        for i in range(game.numPlayers):
            layout.addRow(QLabel('%s %i' % ('Player ', i)))
            self.texts.append(QLineEdit())
            layout.addRow(self.texts[i])

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | \
                                   QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        
        layout.addRow(buttons)
        self.setLayout(layout)
    
    def accept(self):
        for i in range(game.numPlayers):
            text = self.texts[i].text()
            game.playerNames.append(text)
        super(PlayerNames, self).accept()


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
        
        mapSize = QGroupBox('Select Map Size')
        lbl = QLabel('Select Map Size')
        box = QVBoxLayout()
        b1 = QRadioButton('Small')
        b2 = QRadioButton('Medium')
        b3 = QRadioButton('Huge')
        self.btns = [b1,b2,b3]
        b1.setChecked(True)
        box.addWidget(b1)
        box.addWidget(b2)
        box.addWidget(b3)
        mapSize.setLayout(box)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Cancel)
        btn1 = QPushButton('Single Player', self)
        btn2 = QPushButton('Multi Player', self)
        btn1.clicked.connect(self.single)
        btn2.clicked.connect(self.multi)
        buttons.addButton(btn1, QDialogButtonBox.ActionRole)
        buttons.addButton(btn2, QDialogButtonBox.ActionRole)
        buttons.rejected.connect(self.reject)

        layout.addRow("Number Of Units", self.numUnits)
        layout.addRow("Number Of Players", self.numPlayers)
        layout.addRow(mapSize)
        layout.addRow(buttons)
        self.setLayout(layout)

    def single(self):
        game.numUnits = self.numUnits.value()
        game.numPlayers = self.numPlayers.value()
        for i in range(len(self.btns)):
            if self.btns[i].isChecked():
                game.mapSize = i
        super(NewGameDialog, self).accept()

    def multi(self):
        game.mode = 'multi'
        self.single()

# user is displayed commands for a unit
class UnitActionForm(QDialog):
    def __init__(self, parent=None):
        super(UnitActionForm, self).__init__(parent)
        methods = (
                ('Cancel', self.cancelAction),
                ('Move', self.moveAction),
                ('Attack', self.attackAction),
                ('Build farm', lambda: self.buildAction('farm')),
                ('Build tank', lambda: self.buildAction('tank')),
                ('Build wall', lambda: self.buildAction('wall')),
                ('Build settlement', lambda: self.buildAction('settlement')),
            )
        
        layout = QFormLayout()
        actionButtonGroupBox = QWidget()
        abLayout = QVBoxLayout()
        abLayout.setContentsMargins(10,20,10,10)
        for title, action in methods:
            btn = QPushButton(title, self)
            btn.setMinimumSize(40,25)
            btn.clicked.connect(action)
            abLayout.addWidget(btn)
        actionButtonGroupBox.setLayout(abLayout)
        layout.addRow(actionButtonGroupBox)
        self.setLayout(layout)

    def updateTitle(self):
        mainW.bottomDock.updateTitle()

    def buildAction(self, building):
        self.hide()
        if game.buildAction(building):
            self.delete()
        else:
            self.show()
    
    def recruitAction(self, unit):
        self.hide()
        if game.recruitAction(unit):
            self.delete()
        else:
            self.show()
    
    def moveAction(self):
        self.hide()
        if game.moveAction(self.updateTitle):
            self.delete()
        else:
            self.show()

    def attackAction(self):
        self.hide()
        if game.attackAction():
            self.delete()
        else:
            self.show()
    
    def cancelAction(self):
        self.delete()
    
    def delete(self):
        if game.singletonObject:
            game.singletonObject = None
            self.done(0)

class BottomDock(QDockWidget):
    def __init__(self, parent):
        super(BottomDock, self).__init__(parent)

        self.title = QLabel()
        self.title.setIndent(20)
        self.updateTitle()
        self.setTitleBarWidget(self.title)

        layout = QFormLayout()
        self.distButton = QPushButton("Pass")
        self.nextTurnButton = QPushButton("Next Turn")
        self.nextTurnButton.clicked.connect(self.nextTurnAction)

        turnControlButtonGroupBox = QWidget()
        tcLayout = QHBoxLayout()
        mar = tcLayout.contentsMargins().bottom()
        tcLayout.setContentsMargins(mar, 0, mar, mar)
        tcLayout.addWidget(self.nextTurnButton)
        turnControlButtonGroupBox.setLayout(tcLayout)

        layout.addRow(turnControlButtonGroupBox)
        bottomDockWidget = QWidget()
        bottomDockWidget.setLayout(layout)
        self.setWidget(bottomDockWidget)

    def updateTitle(self):
        if game.mode=='single':
            self.title.setText("Unit: %d   Turn: %d" % (game.currentPlayer.printableUnitIndex, game.turn))
        else:
            self.title.setText("Player: %s   Turn: %d" % (game.currentPlayer.name, game.turn))

    def nextTurnAction(self):
        if game.nextTurnAction():
            if game.singletonObject:
                game.singletonObject.delete()
            self.updateTitle()
            self.enableButtons()

    def disableButtons(self):
        self.distButton.setEnabled(False)

    def enableButtons(self):
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
            if game.mode == 'multi':
                names = PlayerNames(self) #get player names
                if not names.exec_():
                    self.close()
                    sys.exit()

            game.start()

        [[self.mainScene.addItem(hex) for hex in row] for row in game.map.tiles]

        self.setCentralWidget(self.mainView)
        self.mainView.show()
        game.nextPlayerAction()

if __name__ == "__main__":
    global mainW
    app = QApplication([])

    window = MainWindow()
    mainW = window
    window.setWindowTitle("Super peli!")
    window.show()
    Hexagon.showUnitDialog = _showUnitDialog
    Hexagon.mapSize = game.mapSize
    # Have to do this manually here, after everything has been initialized,
    # because otherwise, the current unit might not be visible the first time
    # you start the game
    #game.currentPlayer.currentUnit.tile.ensureVisible()

    app.exec_()
