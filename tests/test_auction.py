import unittest
from freeride.double_auction import UnitAgent, UnitDemand, UnitSupply, DoubleAuction

class TestDoubleAuction(unittest.TestCase):

    def setUp(self):

        #agent_a = UnitAgent(8, 1)
        #agent_b = UnitAgent(9, 0)
        #agent_c = UnitAgent(4, 1)
        #agent_d = UnitAgent(5, 0)
        agent_a = UnitSupply(8)
        agent_b = UnitDemand(9)
        agent_c = UnitSupply(4)
        agent_d = UnitDemand(5)
        self.agents = agent_a, agent_b, agent_c, agent_d

    def test_double_auction(self):

        auction = DoubleAuction(*self.agents)
        price0, price1 = auction.p
        q = auction.q

        self.assertTrue(q == 1)
        self.assertTrue(price0 == 5)
        self.assertTrue(price1 == 8)
        
    def tearDown(self):
        pass
