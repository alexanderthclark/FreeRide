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

    def test_multi_unit_agents(self):
        seller = UnitSupply(4, 5)
        buyer = UnitDemand(7, 6)
        auction = DoubleAuction(seller, buyer)
        price0, price1 = auction.p
        self.assertEqual(auction.q, 2)
        self.assertEqual(price0, 5)
        self.assertEqual(price1, 6)

    def test_multi_unit_multiple_agents(self):
        sellers = (UnitSupply(1, 2), UnitSupply(3, 4))
        buyers = (UnitDemand(6, 5), UnitDemand(4, 3))
        auction = DoubleAuction(*sellers, *buyers)
        price0, price1 = auction.p
        self.assertEqual(auction.q, 3)
        self.assertEqual(price0, 3)
        self.assertEqual(price1, 4)
        
    def tearDown(self):
        pass
