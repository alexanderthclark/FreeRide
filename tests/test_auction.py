import unittest
from freeride.double_auction import UnitAgent, DoubleAuction

class TestDoubleAuction(unittest.TestCase):

    def setUp(self):

        agent_a = UnitAgent(8, 1)
        agent_b = UnitAgent(9, 0)
        agent_c = UnitAgent(4, 1)
        agent_d = UnitAgent(5, 0)
        self.agents = agent_a, agent_b, agent_c, agent_d

    def test_double_auction(unittest.TestCase):

        auction = DoubleAuction(*self.agents)
        price0, price1 = auction.p
        q = auction.q

        self.assertTrue(q == 1)
        self.assertTrue(price0 == 5)
        self.assertFalse(price1 == 8)
        
    def tearDown(self):
        pass
