import unittest
from freeride.curves import Affine

class TestAffine(unittest.TestCase):

    def setUp(self):
        self.slope = -2
        self.intercept = 12
        self.demand = Affine(self.intercept, self.slope, inverse = False)

    def test_q_intercept(self):
        #self.assertTrue(self.demand.intercept == 6)
        pass
        
    def tearDown(self):
        pass
