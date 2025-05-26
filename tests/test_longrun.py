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


class TestCostProfitPlot(unittest.TestCase):
    def test_cost_profit_plot_respects_passed_axes(self):
        import matplotlib.pyplot as plt
        from unittest.mock import patch
        from freeride.base import AffineElement

        fig, (ax0, ax1) = plt.subplots(1, 2)
        plt.sca(ax0)

        c = Cost(1, 0, 1)

        with patch.object(Cost, "marginal_cost", return_value=AffineElement(0, 1)):
            c.cost_profit_plot(4, ax=ax1)

        self.assertEqual(len(ax0.lines), 0)
        self.assertGreaterEqual(len(ax1.lines), 5)


if __name__ == "__main__":
    unittest.main()
