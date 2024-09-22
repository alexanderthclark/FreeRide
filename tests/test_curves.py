import unittest
from freeride.curves import Affine, Demand

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

class TestDemand(unittest.TestCase):

    def setUp(self):

        self.d1 = Demand(12,-2)
        self.d2 = Demand.from_formula('p = 12 - q')

    def shifts(self):

        new_d = self.d1.vertical_shift(1, inplace=False)
        self.assertTrue(new_d.p(0) == 13)

        self.d1.horizontal_shift(1, inplace=True)
        self.assertTrue(self.d1.q(0)==7)
