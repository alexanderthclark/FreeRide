import unittest

import matplotlib
matplotlib.use("Agg")

from freeride.curves import Demand
from freeride.costs import Cost
from freeride.equilibrium import LongRunCompetitiveEquilibrium


class TestLongRunCompetitiveEquilibrium(unittest.TestCase):
    def test_basic_attributes(self):
        demand = Demand(10, -1)
        cost = Cost(1, 0, 1)
        lr = LongRunCompetitiveEquilibrium(demand, cost)
        self.assertAlmostEqual(lr.p, 2.0)
        self.assertAlmostEqual(lr.firm_q, 1.0)
        self.assertAlmostEqual(lr.market_q, 8.0)
        self.assertAlmostEqual(lr.n_firms, 8.0)
