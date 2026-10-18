"""Economic areas measured from the polygons actually drawn in market figures."""

import unittest

import matplotlib
matplotlib.use("Agg")
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import numpy as np

from freeride.curves import Demand, Supply
from freeride.equilibrium import Equilibrium
from freeride.plotting import CONSUMER_FILL, PRODUCER_FILL, REVENUE_FILL


def filled_area(ax, color=None):
    """Measure filled polygons with the shoelace formula, without curve algebra."""
    area = 0.0
    for collection in ax.collections:
        if color is not None:
            facecolors = collection.get_facecolor()
            if not len(facecolors) or not np.allclose(facecolors[0, :3], colors.to_rgb(color)):
                continue
        for path in collection.get_paths():
            x, y = path.vertices.T
            area += abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1))) / 2
    return area


class TestMarketWelfareFigures(unittest.TestCase):
    # D: P=20-Q; S: P=5+Q/2. Free equilibrium is (Q,P)=(10,10).
    cases = (
        ({}, 50, 25, 0, 0),
        ({"tax": 3}, 32, 16, 24, 3),
        ({"tax": -3}, 72, 36, 0, 3),
        ({"ceiling": 8}, 54, 9, 0, 12),
        ({"floor": 12}, 32, 40, 0, 3),
    )

    def tearDown(self):
        plt.close("all")

    def test_consumer_producer_and_tax_areas_match_hand_calculations(self):
        for policy, consumer, producer, revenue, _ in self.cases:
            with self.subTest(policy=policy):
                market = Equilibrium(Demand(20, -1), Supply(5, .5), **policy)
                _, ax = plt.subplots()
                market.plot(ax=ax, surplus=True)
                self.assertAlmostEqual(filled_area(ax, CONSUMER_FILL), consumer)
                self.assertAlmostEqual(filled_area(ax, PRODUCER_FILL), producer)
                self.assertAlmostEqual(filled_area(ax, REVENUE_FILL), revenue)
                self.assertAlmostEqual(market.consumer_surplus, consumer)
                self.assertAlmostEqual(market.producer_surplus, producer)

    def test_deadweight_loss_polygons_match_hand_calculations(self):
        for policy, _, _, _, loss in self.cases:
            with self.subTest(policy=policy):
                market = Equilibrium(Demand(20, -1), Supply(5, .5), **policy)
                _, ax = plt.subplots()
                market._plot_closed_dwl(ax)
                self.assertAlmostEqual(filled_area(ax), loss)
                self.assertAlmostEqual(market.dwl, loss)

    def test_deadweight_loss_crosses_piecewise_boundaries_once(self):
        demand = Demand(20, -1) + Demand(10, -1)
        # Demand changes slope at Q=10. Each policy crosses that boundary.
        # Tax: integral_8^10(20-1.5Q) + integral_10^15(15-Q) = 25.5.
        # Subsidy: integral_(20/3)^10(3Q-20) + integral_10^12(2.5Q-15) = 125/3.
        cases = ((Supply(0, .5), 8, 25.5), (Supply(0, 2), -15, 125 / 3))
        for supply, tax, loss in cases:
            with self.subTest(tax=tax):
                market = Equilibrium(demand, supply, tax=tax)
                _, ax = plt.subplots()
                market._plot_closed_dwl(ax)
                self.assertAlmostEqual(filled_area(ax), loss)

    def test_supplied_axes_keep_the_users_limits_and_labels(self):
        _, ax = plt.subplots()
        ax.set(xlim=(2, 18), ylim=(4, 16), xlabel="Units per week",
               ylabel="Dollars per unit", title="A binding ceiling")
        market = Equilibrium(Demand(20, -1), Supply(5, .5), ceiling=8)
        self.assertIs(market.plot(ax=ax, surplus=True), ax)
        self.assertEqual(ax.get_xlim(), (2, 18))
        self.assertEqual(ax.get_ylim(), (4, 16))
        self.assertEqual(ax.get_xlabel(), "Units per week")
        self.assertEqual(ax.get_ylabel(), "Dollars per unit")
        self.assertEqual(ax.get_title(), "A binding ceiling")

    def test_steep_supply_keeps_a_finite_view_around_equilibrium(self):
        market = Equilibrium(Demand(100, -.01), Supply(1, 1000))
        ax = market.plot(surplus=True)
        x0, x1 = ax.get_xlim()
        y0, y1 = ax.get_ylim()
        self.assertTrue(np.isfinite([x0, x1, y0, y1]).all())
        self.assertEqual((x0, y0), (0, 0))
        self.assertGreater(x1, market.q)
        self.assertGreater(y1, market.p)
        # The distant demand intercept is 10,000 units; it must not flatten
        # the visible equilibrium, which trades about 0.099 units.
        self.assertLess(x1, 10 * market.q)
        self.assertLess(y1, 5 * market.p)
        for line in ax.lines:
            self.assertTrue(np.isfinite(line.get_xydata()).all())
        for collection in ax.collections:
            for path in collection.get_paths():
                self.assertTrue(np.isfinite(path.vertices).all())
