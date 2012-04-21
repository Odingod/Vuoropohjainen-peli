import unittest
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

		
class DummyGame():

	def __init__(self):
		self.mode=None
	

if __name__ == '__main__':
	suite = unittest.TestLoader().loadTestsFromTestCase(TestPlayer)
	unittest.TextTestRunner(verbosity=2).run(suite)
