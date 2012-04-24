import unittest, sys
from Units import *
from save import *
from Map import *
from Players import *
from Settlement import *
from PySide.QtGui import QApplication
from application import *
import random
import StringIO
class TestPlayer(unittest.TestCase):

	def setUp(self):
		self.app=QApplication([])
		self.dg=DummyGame()
		self.p1=Player(self.dg)
		self.p2=Player(self.dg)
		self.m=Map()
		self.m.createSquareMap(3,[self.p1, self.p2])
		print "created"
	def test_unitnumber(self):
		i=0
		for unit in self.m.units:
			if unit.owner == self.p1 and unit.getId() == 'tank':
				i=i+1
		
		self.assertEqual(i,3)
		
	def tearDown(self):
		pass


#test created by Eetu Haavisto
class TestSettlement(unittest.TestCase):
    def setUp(self):
        self.dg=DummyGame()
        self.p1=HumanPlayer(self.dg)
        self.settlement = Settlement(population=1500, owner=self.p1, map=DummyMap())
    def test_population(self):
        self.assertEqual(1500, self.settlement.population, "Population initialized incorrectly")
        self.settlement.build("farm")
        self.assertEqual(1600, self.settlement.population, "Building a farm doesn't increase population")
    def test_recruitment(self):
        self.assertFalse(self.settlement.do_recruit(DummyUnit, self.p1, DummyTile(), 10000), "It's possible to recruit a unit too expensive")
        self.assertTrue(self.settlement.do_recruit(DummyUnit, self.p1, DummyTile(), 500), "Recruitment doesn't work")
        self.assertEqual(500, self.p1.treasury, "Recruitment doesn't affect owner's treasury")
    def tearDown(self):
        pass

#test created by Petri Niemela
class TestUnitSaving(unittest.TestCase):
    def setUp(self):
        pass
        
    def test_save(self):
        testunit = Unit(id=123, image="DummyImage", hp=99, moves=(1,1), owner=None)
        self.assertEqual(saveable(None), None, "Saving None failed!")
        try:
            result = saveable(testunit)
            self.assertEqual(result["moves"], (1,1), "Saving failed! Wrong 'moves' vector")
            self.assertEqual(result["owner"], None, "Saving failed! Wrong owner")
            self.assertEqual(result["id"], 123, "Saving failed! Wrong ID")
            self.assertEqual(result["hp"], 99, "Saving failed! Wrong Hp")
        except NotSaveableException:
            self.assertTrue(False, "Saving failed! NotSaveableException raised")
            
    def test_save_fail(self):
        failed = False
        try: 
            saveable( DummyTile() )
        except NotSaveableException:
            failed = True
        self.assertTrue(failed, "Wrong parameter didn't raise right exception")

    def tearDown(self):
        pass

#Jesse Makkonen
class TestUnits(unittest.TestCase):
    def setUp(self):
        random.seed(1337)
        self.game = Game()
        self.player = HumanPlayer(self.game)
        self.game.map.createSquareMap(self.game.numUnits, [self.player], 50, 1)
        self.output = StringIO.StringIO()
        self.old_output = sys.stdout
        sys.stdout = self.output
    def testMove(self):
        try:
            for unit in self.game.map.units:
                unit.move(0,3)
                unit.move(2,0)
        except IndexError:
            pass
        string = self.output.getvalue().strip()
        string = string.split('\n')
        for i in range(5):
            self.assertTrue("can't" in string[i])
        self.assertEqual(100, self.game.map.units[0].hp)
        self.assertEqual(7, len(string))
        self.game.map.units[0].takeDamage(50)
        self.assertEqual(50, self.game.map.units[0].hp)
        self.game.map.units[0].takeDamage(100)
        self.assertEqual(10, self.game.map.units[0].hp)
        sys.stdout = self.old_output
    def tearDown(self):
        pass

class DummyGame():
    def __init__(self):
        self.mode=None
    def nextPlayerAction(self):
        pass
class DummyUnit():
    def __init__(self, owner, tile):
        pass
class DummyTile():
    def addUnit(self, unit):
        pass
class DummyMap():
    def __init__(self):
        self.units = []

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    unittest.TextTestRunner(verbosity=2).run(suite)
    
