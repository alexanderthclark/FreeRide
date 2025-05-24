import unittest
from freeride.curves import Demand
from freeride.costs import Cost
from freeride.monopoly import Monopoly


class TestMonopoly(unittest.TestCase):
    def test_basic_outcome(self):
        demand = Demand(10, -1)
        cost = Cost(0, 2)
        m = Monopoly(demand, cost)
        self.assertAlmostEqual(m.q, 4.0)
        self.assertAlmostEqual(m.p, 6.0)
        self.assertAlmostEqual(m.profit, 16.0)

    def test_piecewise_demand_zero_cost(self):
        """Profit maximization with piecewise demand and zero cost."""
        demand = Demand([10, 5], [-1, -1])
        cost = Cost(0, 0)
        m = Monopoly(demand, cost)
        self.assertAlmostEqual(m.q, 7.5)
        self.assertAlmostEqual(m.p, 3.75)
        self.assertAlmostEqual(m.profit, 28.125)


if __name__ == "__main__":
    unittest.main()
