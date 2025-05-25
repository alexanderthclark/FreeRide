import unittest
from freeride.curves import Demand, Supply
from freeride.equilibrium import Market


class TestMarketPerfectCurve(unittest.TestCase):

    def test_market_with_horizontal_supply(self):
        demand = Demand(10, -1)
        supply = Supply(5, 0)
        market = Market(demand, supply)
        self.assertAlmostEqual(market.p, 5.0)
        self.assertAlmostEqual(market.q, 5.0)


    def test_market_with_vertical_demand(self):
        demand = Demand(5, 0, inverse=False)
        supply = Supply(0, 1)
        market = Market(demand, supply)
        self.assertAlmostEqual(market.p, 5.0)
        self.assertAlmostEqual(market.q, 5.0)

