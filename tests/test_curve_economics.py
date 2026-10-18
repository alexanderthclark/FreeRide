"""Hand-calculated welfare, elasticity, and piecewise-curve regressions."""

import unittest

import matplotlib.pyplot as plt
import numpy as np

from freeride.affine import AffineElement
from freeride.curves import Demand, Supply
from freeride.equilibrium import Equilibrium


class TestSurplusBoundaries(unittest.TestCase):
    def test_free_goods_consumer_surplus(self):
        # The triangle below P=10-Q has area 10*10/2.
        self.assertAlmostEqual(Demand(10, -1).consumer_surplus(0), 50)

    def test_aggregate_consumer_surplus(self):
        demand = Demand(10, -1) + Demand(5, -1)
        # Sum the two consumers' triangular surplus areas at each price.
        for price, expected in [(0, 62.5), (2.5, 31.25), (5, 12.5), (10, 0)]:
            with self.subTest(price=price):
                self.assertAlmostEqual(demand.consumer_surplus(price), expected)

    def test_quantity_limited_consumer_surplus(self):
        demand = Demand(10, -1) + Demand(5, -1)
        # Only the first segment supplies quantities 0..4: integral(6-Q)=16.
        self.assertAlmostEqual(demand.consumer_surplus(4, q=4), 16)
        self.assertEqual(demand.consumer_surplus(4, q=0), 0)

    def test_aggregate_producer_surplus(self):
        supply = Supply(0, 1) + Supply(2, 1)
        # At P=4 the suppliers produce 4 and 2 units: PS=4*4/2+2*2/2.
        self.assertAlmostEqual(supply.producer_surplus(4), 10)
        # Over quantities 0..3, the areas are 6 and 1.75.
        self.assertAlmostEqual(supply.producer_surplus(4, q=3), 7.75)

    def test_piece_selection_includes_full_quantity_range(self):
        demand = Demand(10, -1) + Demand(5, -1)
        for quantity, price in [(0, 10), (5, 5), (15, 0)]:
            with self.subTest(quantity=quantity):
                piece = demand._get_active_piece(quantity)
                self.assertIsNotNone(piece)
                self.assertAlmostEqual(demand(quantity), price)
                self.assertAlmostEqual(piece(quantity), demand(quantity))
        self.assertTrue(np.isnan(demand(15.1)))


class TestSurplusShading(unittest.TestCase):
    def tearDown(self):
        plt.close("all")

    @staticmethod
    def shaded_area(ax):
        """Measure the actual filled polygons, independently of curve formulas."""
        area = 0.0
        for collection in ax.collections:
            for path in collection.get_paths():
                x, y = path.vertices.T
                area += abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1))) / 2
        return area

    def test_shaded_areas_match_textbook_surplus(self):
        cases = [
            (Demand(10, -1), 0, None, 50),
            (Demand(10, -1) + Demand(5, -1), 0, None, 62.5),
            (Demand(10, -1) + Demand(5, -1), 4, (0, 4), 16),
            (Supply(0, 1) + Supply(2, 1), 4, None, 10),
            (Supply(0, 1) + Supply(2, 1), 4, (0, 3), 7.75),
        ]
        for curve, price, quantity_range, expected in cases:
            with self.subTest(curve=repr(curve), price=price, q=quantity_range):
                _, ax = plt.subplots()
                curve.plot_surplus(price, q=quantity_range, ax=ax)
                self.assertAlmostEqual(self.shaded_area(ax), expected)
                quantity = quantity_range[1] if quantity_range else None
                self.assertAlmostEqual(abs(curve.surplus(price, quantity)), expected)
                plt.close(ax.figure)

    def test_tax_and_subsidy_deadweight_loss_shading(self):
        # A wedge of 2 changes Q by 1, giving DWL = 2*1/2 in either direction.
        for tax in (-2, 2):
            with self.subTest(tax=tax):
                market = Equilibrium(Demand(10, -1), Supply(0, 1), tax=tax)
                _, ax = plt.subplots()
                market._plot_closed_dwl(ax)
                self.assertAlmostEqual(self.shaded_area(ax), 1)
                plt.close(ax.figure)


class TestPriceElasticity(unittest.TestCase):
    def test_demand_elasticity_at_interior_and_zero_price(self):
        demand = Demand(12, -2)
        self.assertAlmostEqual(demand.price_elasticity(4), -0.5)
        self.assertEqual(demand.price_elasticity(0), 0)
        self.assertEqual((demand + Demand(6, -1)).price_elasticity(0), 0)

    def test_supply_elasticity(self):
        self.assertAlmostEqual(Supply(2, 1).price_elasticity(4), 2)
        self.assertAlmostEqual(AffineElement(2, 1).midpoint_elasticity(3, 5), 2)
        # A supply ray through the origin has unit elasticity, including its limit at zero.
        self.assertEqual(Supply(0, 2).price_elasticity(4), 1)
        self.assertEqual(Supply(0, 2).price_elasticity(0), 1)

    def test_exact_and_noisy_kinks_at_different_scales(self):
        for scale in (1e-6, 1, 1e6):
            demand = Demand(12 * scale, -1) + Demand(6 * scale, -0.5)
            for price in (6 * scale, (0.1 + 0.2) * 20 * scale):
                with self.subTest(scale=scale, price=price):
                    with self.assertRaisesRegex(ValueError, "kink point"):
                        demand.price_elasticity(price)

    def test_nearby_prices_have_one_sided_elasticities(self):
        demand = Demand(12, -1) + Demand(6, -0.5)
        below, above = 6 - 1e-7, 6 + 1e-7
        self.assertAlmostEqual(demand.price_elasticity(below), -3 * below / (24 - 3 * below))
        self.assertAlmostEqual(demand.price_elasticity(above), -above / (12 - above))

    def test_invalid_prices_and_delta_have_helpful_errors(self):
        demand = Demand(10, -1)
        with self.assertRaisesRegex(ValueError, "Negative price"):
            demand.price_elasticity(-1)
        for delta in (0, -1):
            with self.subTest(delta=delta):
                with self.assertRaisesRegex(ValueError, "delta must be positive"):
                    demand.price_elasticity(5, delta=delta)


class TestMarginalRevenueInverse(unittest.TestCase):
    def test_inverse_uses_quantity_domain(self):
        # P=20-4Q gives MR=20-8Q, with quantity domain [0,5].
        marginal_revenue = Demand(20, -4).marginal_revenue()
        for price, quantity in [(20, 0), (12, 1), (0, 2.5), (-20, 5)]:
            with self.subTest(price=price):
                self.assertAlmostEqual(marginal_revenue.q(price), quantity)
                self.assertAlmostEqual(marginal_revenue(quantity), price)

    def test_direct_evaluation_agrees_with_active_piece_at_kink(self):
        marginal_revenue = (Demand(20, -1) + Demand(10, -0.5)).marginal_revenue()
        # Use the piece to the right in quantity at Q=10, where MR jumps.
        self.assertAlmostEqual(marginal_revenue(10), 20 / 3)
        self.assertAlmostEqual(marginal_revenue._get_active_piece(10)(10), 20 / 3)

    def test_aggregate_inverse_includes_roundoff_at_maximum_quantity(self):
        marginal_revenue = (Demand(20, -1) + Demand(10, -0.5)).marginal_revenue()
        # The final segment has MR=(40-2Q)/3 and ends at Q=40.
        self.assertAlmostEqual(marginal_revenue.q(-40 / 3), 40)
        # A price genuinely beyond that segment still has no inverse quantity.
        self.assertEqual(marginal_revenue.q(-40 / 3 - 1e-8), 0)
