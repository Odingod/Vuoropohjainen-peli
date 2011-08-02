from Units import Unit

class Player:
    def __init__(self,game):
        self.myTurn=False
        self.game=game
        
    
    def doTurn(self):
        self.myTurn=True
    
    def endTurn(self):
        self.game.nextPlayerAction()
    
    def cycleUnits(self):
        try:
             self.currentUnit.tile.setChosen(False)
        except AttributeError:
            pass
        self.unitIndex += 1
        if self.unitIndex == self.game.numUnits:
            self.unitIndex = -1 
            self.currentUnit = None
        elif self.game.map.units[self.unitIndex].owner != self:
            self.cycleUnits()
        else:
            self.currentUnit = self.game.map.units[self.unitIndex]
        
class HumanPlayer(Player):
    def __init__(self,game):
        Player.__init__(self,game)
        self.unitIndex = -1
        self.currentUnit = None
    
    def doTurn(self):
        Player.doTurn(self)
        self.unitIndex=-1
        self.nextUnitAction()
        
    

    
    def nextUnitAction(self, *args):
        self.cycleUnits()
        if self.currentUnit:
            self.currentUnit.tile.setChosen(True)
            #self.currentUnit.tile.ensureVisible()
        else:
            self.endTurn()
    
    def endTurn(self):
        Player.endTurn(self)
    
    

class AIPlayer(Player):
    def __init__(self,game):
        Player.__init__(self,game)
    
    def doTurn(self):
        self.unitIndex = -1
        self.cycleUnits()
        neighboring=self.currentUnit.tile.getNeighborsI()
        for neighbour in neighboring:
            try:
                if self.currentUnit.tile.map.tiles[neighbour[0]][neighbour[1]].terrain.canHoldUnit:
                    Unit.move(self.currentUnit,neighbour[0],neighbour[1])
                    break
            except (IndexError, TypeError):
                pass
        self.endTurn()