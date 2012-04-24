import unittest, sys
from Map import *
from Players import *
from PySide.QtGui import QApplication
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
        from Settlement import *
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
    
