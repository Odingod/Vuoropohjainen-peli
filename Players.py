class Player:
    def __init__(self,game):
        self.myTurn=False
        self.game=game
        
    
    def doTurn(self):
        self.myTurn=True
    
    def endTurn(self):
        self.game.nextPlayerAction()
        
class HumanPlayer(Player):
    def __init__(self,game):
        Player.__init__(self,game)
        self.unitIndex = -1
        self.currentUnit = None
    
    def doTurn(self):
        Player.doTurn(self)
        self.unitIndex=-1
        self.nextUnitAction()
        
    
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
            print 'found unit'
            self.currentUnit = self.game.map.units[self.unitIndex]
    
    def nextUnitAction(self, *args):
        self.cycleUnits()
        if self.currentUnit:
            self.currentUnit.tile.setChosen(True)
            self.currentUnit.tile.ensureVisible()
        else:
            self.endTurn()
    
    def endTurn(self):
        Player.endTurn(self)
    
    

class AIPlayer(Player):
    def __init__(self,game):
        Player.__init__(self,game)
    
    def doTurn(self):
        self.endTurn()