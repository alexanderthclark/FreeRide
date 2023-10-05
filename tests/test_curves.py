import unittest
from microecon.curves import Demand, Supply

class TestDemand(unittest.TestCase):

    def setUp(self):
        self.slope = -2
        self.intercept = 12
        self.demand = Demand(self.intercept, self.slope)

    def test_q_intercept(self):
        self.assertTrue(self.demand.q_intercept == 6)

    # for intentional failure
    #def test_break(self):
    #   self.assertTrue(False)

    def tearDown(self):
        pass
