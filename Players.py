class Player:
    count = 0
    loadedPlayers = {}

    def __init__(self, game):
        Player.count += 1
        self.id = Player.count
        self.myTurn = False
        self.game = game
        self.printableUnitIndex = 0

    def __saveable__(self):
        d = {}

        d['id'] = self.id
        d['type'] = 'human' if isinstance(self, HumanPlayer) else 'ai'
        d['myTurn'] = self.myTurn
        d['unitIndex'] = self.unitIndex
        d['printableUnitIndex'] = self.printableUnitIndex
        
        return d

    @classmethod
    def __load__(cls, d, game):
        if cls.loadedPlayers.has_key(d['id']):
            return cls.loadedPlayers[d['id']]

        if d['type'] == 'human':
            p = HumanPlayer(game)
        else:
            p = AIPlayer(game)

        p.id = d['id']
        p.myTurn = d['myTurn']
        p.unitIndex = d['unitIndex']
        p.printableUnitIndex = d['printableUnitIndex']
        
        if p.myTurn:
            p.unitIndex -= 1
            p.printableUnitIndex -= 1
            p.cycleUnits() # sets p.currentUnit

        cls.loadedPlayers[p.id] = p

        return p
    
    def doTurn(self):
        self.myTurn = True
    
    def endTurn(self):
        self.myTurn = False
        self.game.nextPlayerAction()
    
    def cycleUnits(self):
        print self.game.map.units
        try:
            self.currentUnit.tile.setChosen(False)
        except AttributeError:
            pass
        self.unitIndex += 1
        if self.unitIndex >= len(self.game.map.units):
            print 'full', self.unitIndex
            self.unitIndex = -1 
            self.printableUnitIndex = 0
            self.currentUnit = None
        elif self.game.map.units[self.unitIndex].owner != self:
            print 'enemy', self.unitIndex, self.game.map.units[self.unitIndex], self.game.map.units[self.unitIndex].owner
            self.cycleUnits()
        else:
            print 'own', self.unitIndex
            self.currentUnit = self.game.map.units[self.unitIndex]
            self.printableUnitIndex += 1
        
class HumanPlayer(Player):
    def __init__(self, game):
        Player.__init__(self, game)
        self.unitIndex = -1
        self.currentUnit = None
    
    def doTurn(self):
        Player.doTurn(self)
        self.unitIndex = -1
        self.nextUnitAction()
    
    def nextUnitAction(self, *args):
        self.cycleUnits()
        print 'unit', self.currentUnit
        print 'index', self.unitIndex
        if self.currentUnit:
            self.currentUnit.tile.setChosen(True)
            self.currentUnit.tile.ensureVisible()
        else:
            self.endTurn()
    
    def endTurn(self):
        print 'ending turn'
        Player.endTurn(self)
    
class AIPlayer(Player):
    def __init__(self, game):
        Player.__init__(self, game)
    
    def doTurn(self):
        self.unitIndex = -1
        self.cycleUnits()
        while self.currentUnit:
            if self.currentUnit.id == "settlement":
                self.currentUnit.recruit("tank")
            self.currentUnit.tile.ensureVisible()
            import time
            
            print 'sleeping'
            time.sleep(1)
            neighboring = self.currentUnit.tile.getNeighborsI()
            for neighbour in neighboring:
                try:
                    if self.currentUnit.tile.map.tiles[neighbour[0]][neighbour[1]].terrain.canHoldUnit:
                        self.currentUnit.move(neighbour[0], neighbour[1],
                                ai=True)
                        self.currentUnit.tile.setChosen(True)
                        break
                except (IndexError, TypeError):
                    pass
            
            self.cycleUnits()
        self.endTurn()
