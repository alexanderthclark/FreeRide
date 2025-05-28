import unittest
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from freeride.curves import Demand
from freeride.revenue import Revenue, MarginalRevenue


class TestRevenueUtilities(unittest.TestCase):
    def setUp(self):
        self.demand = Demand(12, -2)
        self.revenue = self.demand.total_revenue()

    def test_plot_returns_axes(self):
        ax = self.revenue.plot()
        self.assertIsInstance(ax, plt.Axes)

    def test_marginal_revenue(self):
        mr = self.revenue.marginal_revenue()
        self.assertIsInstance(mr, MarginalRevenue)
        self.assertAlmostEqual(mr(2), 12 - 4 * 2)
        self.assertIsInstance(mr.plot(), plt.Axes)


if __name__ == "__main__":
    unittest.main()
