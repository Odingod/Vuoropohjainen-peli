

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
        import time
        while self.currentUnit:
            print "CURRENTUNIT", self.currentUnit
            self.currentUnit.tile.ensureVisible()
            
            if self.currentUnit.id == "settlement":
                self.currentUnit.recruit("tank")
            
            elif self.currentUnit.id == "tank":
                for unit in self.game.map.units:
                    if unit.owner != self:
                        if self.currentUnit.attack(unit):
                            pass
                        elif unit.id == "settlement":
                            location_i, location_j = unit.tile.i, unit.tile.j
                            route = self.currentUnit.tile.getRoute(location_i, location_j)
                            for i in range(max(self.currentUnit.moves)-1):
                                route.pop()
                            tile = route.pop()
                            self.currentUnit.move(tile.i, tile.j, ai=True)
                    
            elif self.currentUnit.id == "builder":      
                print "BUILDER"    
                neighboring = self.currentUnit.tile.getBoardNeighbors()
                for neighbour in neighboring:
                    if self.currentUnit.tile.map.tiles[neighbour[0]][neighbour[1]].units:
                        print "if unit"
                        for unit in self.currentUnit.tile.map.tiles[neighbour[0]][neighbour[1]].units:
                            print "AI, yksikkoja", unit
                            if unit.id == "gold":
                                print "AI:kulta", self.game.map.unused_gold
                                unit.tile.setChosen(True)
                                self.currentUnit.building = "mine"
                                self.currentUnit.doBuild(unit.tile.i, unit.tile.j)
                                print self.game.map.unused_gold, unit
                                self.game.map.unused_gold.remove(unit)
                    '''except (IndexError, TypeError):
                        print "VIRHE, siirrytaan seuraavaan yksikkoon"
                        pass '''
                print self.game.map.units
                min_dist = 100
                nearest = None
                curloc = self.currentUnit.tile
                for gold_place in self.game.map.unused_gold:
                    dist = curloc.distance(gold_place.tile.i, gold_place.tile.j)
                    if dist < min_dist:
                        free = True
                        for unit in gold_place.tile.units:
                            if unit.id == "mine":
                                free = False
                        if free:
                            min_dist = dist
                            nearest = gold_place
                location_i, location_j = nearest.tile.i, nearest.tile.j
                route = self.currentUnit.tile.getRoute(location_i, location_j)
                if not route:
                    pass
                elif len(route)-1 <= max(self.currentUnit.moves):
                    print "IN-range"
                    dest_i, dest_j = route[1].i, route[1].j
                    self.currentUnit.move(dest_i, dest_j, ai=True)
                else:
                    print "OUT-range"
                    for i in range(max(self.currentUnit.moves)-1):
                        route.pop()
                    tile = route.pop()
                    self.currentUnit.move(tile.i, tile.j, ai=True)
                    
                              
            time.sleep(1)                   
            self.cycleUnits()                 
# if self.currentUnit.tile.map.tiles[neighbour[0]][neighbour[1]].terrain.canHoldUnit:
#     self.currentUnit.move(neighbour[0], neighbour[1],
#             ai=True)
#     self.currentUnit.tile.setChosen(True)
#     break
                
            
            
        self.treasury += 100*self.mine_count
        self.endTurn()

