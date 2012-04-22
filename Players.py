

from PySide.QtCore import Qt

class Player:
    count = 0
    loadedPlayers = {}

    def __init__(self, game):
        Player.count += 1
        self.id = Player.count
        self.myTurn = False
        self.game = game
        self.printableUnitIndex = 0
        self.unitCount = 0
        self.doneUnits = set()
        self.defeated = False
        self.mine_count = 0
        self.treasury = 1000
        if game.mode == 'multi':
            self.name = game.playerNames.pop()

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
            print 'enemy', self.unitIndex
            self.cycleUnits()
        else:
            print 'own', self.unitIndex
            self.currentUnit = self.game.map.units[self.unitIndex]
            self.printableUnitIndex += 1

    def unitColor(self):
        unitColors = [Qt.black,Qt.blue, Qt.red, Qt.green, Qt.yellow, Qt.white]
        return unitColors[self.id] if self.id < len(unitColors) else Qt.black

    def printableUnitColor(self):
        unitColors = ['black','blue', 'red', 'green', 'yellow', 'white']
        return unitColors[self.id] if self.id < len(unitColors) else 'black'

    def removeUnit(self, unit):
        self.unitCount -= 1

        if len(filter(lambda x: x.owner == self, self.game.map.units)) == 1:
            self.defeated = True
            # TODO: Actually defeat the player.

class HumanPlayer(Player):
    def __init__(self, game):
        Player.__init__(self, game)
        self.unitIndex = -1
        self.currentUnit = None
    
    def doTurn(self):
        self.doneUnits = set()
        Player.doTurn(self)
        self.unitCount = len(filter(lambda u: u.owner == self, self.game.map.units))
        self.unitIndex = -1
    
    def unitDone(self):
        self.doneUnits.add(self.currentUnit)

        if len(self.doneUnits) >= self.unitCount:
            self.endTurn()
    
    def endTurn(self):
        self.treasury += 100*self.mine_count
        print 100*self.mine_count, "new gold brought into treasury which has now", self.treasury, "gold"
        print 'ending turn'
        Player.endTurn(self)
    
class AIPlayer(Player):
    def __init__(self, game):
        Player.__init__(self, game)
        self.unitIndex = -1

    def unitDone(self):
        pass # Dummy function so we don't have to keep checking it's a human.
    
    def doTurn(self):
        self.unitIndex = -1
        self.cycleUnits()
        while self.currentUnit:
            if self.currentUnit.id == "settlement":
                self.currentUnit.recruit("tank")
                self.cycleUnits()
            self.currentUnit.tile.ensureVisible()
            import time
            
            print 'sleeping'
            time.sleep(1)
            neighboring = self.currentUnit.tile.getNeighborsI()
            for neighbour in neighboring:
                try:
                    if self.currentUnit.tile.map.tiles[neighbour[0]][neighbour[1]].units:
                        for unit in self.currentUnit.tile.map.tiles[neighbour[0]][neighbour[1]].units:
                            print "AI, yksikkoja", unit
                            if unit.id == "gold":
                                print "AI:kulta"
                                self.currentUnit.build('mine')
                            else:
                                self.currentUnit.attack(unit)
                                
                    if self.currentUnit.tile.map.tiles[neighbour[0]][neighbour[1]].terrain.canHoldUnit:
                        self.currentUnit.move(neighbour[0], neighbour[1],
                                ai=True)
                        self.currentUnit.tile.setChosen(True)
                        break
                except (IndexError, TypeError):
                    pass
            
            self.cycleUnits()
        self.treasury += 100*self.mine_count
        self.endTurn()
