import unittest
import numpy as np
from freeride.curves import (
    Affine,
    BaseAffine,
    Demand,
    Supply,
    PPF,
    intersection,
    blind_sum,
    horizontal_sum,
)
from freeride.exceptions import PPFError
from freeride.base import AffineElement

class TestAffine(unittest.TestCase):

    def setUp(self):
        self.slope = -2
        self.intercept = 12
        self.demand = Affine(self.intercept, self.slope, inverse = False)

    def test_q_intercept(self):
        expected = -self.intercept / self.slope  # should be 6 for current values
        self.assertEqual(self.demand.q_intercept, expected)

    def tearDown(self):
        pass


class TestBaseAffine(unittest.TestCase):

    def setUp(self):
        self.intercepts = [12, 6]
        self.slopes = [-2, -1]
        self.curve = BaseAffine(self.intercepts, self.slopes, inverse=False)

    def test_q_intercept_multiple(self):
        expected = [-b / m for b, m in zip(self.intercepts, self.slopes)]
        result = self.curve.q_intercept
        self.assertEqual(result, expected)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)

class TestDemand(unittest.TestCase):

    def setUp(self):

        self.d1 = Demand(12,-2)
        self.d2 = Demand.from_formula('p = 12 - 1*q')

    def test_shifts(self):

        new_d = self.d1.vertical_shift(1, inplace=False)
        self.assertTrue(new_d.p(0) == 13)

        self.d1.horizontal_shift(1, inplace=True)
        self.assertTrue(self.d1.q(0)==7)

    def test_shift_return_types(self):
        horiz = self.d1.horizontal_shift(1, inplace=False)
        self.assertIsInstance(horiz, Demand)

        vert = self.d1.vertical_shift(1, inplace=False)
        self.assertIsInstance(vert, Demand)


class TestCurveHelpers(unittest.TestCase):

    def test_intersection(self):
        line1 = AffineElement(12, -1)
        line2 = AffineElement(0, 2)
        yx = intersection(line1, line2)
        self.assertAlmostEqual(yx[0], 8.0)
        self.assertAlmostEqual(yx[1], 4.0)

    def test_intersection_parallel_raises(self):
        line1 = AffineElement(12, -1)
        line2 = AffineElement(6, -1)
        with self.assertRaises(np.linalg.LinAlgError):
            intersection(line1, line2)

    def test_blind_sum(self):
        l1 = AffineElement(10, -1)
        l2 = AffineElement(5, -1)
        summed = blind_sum(l1, l2)
        self.assertAlmostEqual(summed.intercept, 7.5)
        self.assertAlmostEqual(summed.slope, -0.5)
        self.assertAlmostEqual(summed.q_intercept, 15.0)

    def test_horizontal_sum(self):
        l1 = AffineElement(10, -1)
        l2 = AffineElement(5, -1)
        active, cutoffs, midpoints = horizontal_sum(l1, l2)
        self.assertEqual(cutoffs, [0, 5, 10])
        self.assertEqual(midpoints, [2.5, 7.5, 11])
        self.assertAlmostEqual(active[0].q_intercept, 15.0)
        self.assertAlmostEqual(active[1].q_intercept, 10.0)
        self.assertIsNone(active[2])


class TestSurplusAndRevenue(unittest.TestCase):

    def setUp(self):
        self.demand = Demand(12, -2)
        self.supply = Supply(0, 1)

    def test_consumer_surplus(self):
        self.assertAlmostEqual(self.demand.consumer_surplus(4), 16.0)

    def test_producer_surplus(self):
        self.assertAlmostEqual(self.supply.producer_surplus(4), 8.0)

    def test_total_revenue(self):
        revenue_curve = self.demand.total_revenue()
        self.assertAlmostEqual(revenue_curve(4), 16.0)


class TestCurveEdgeCases(unittest.TestCase):
    """Edge case tests for curve utilities."""

    def test_upward_sloping_demand_raises(self):
        with self.assertRaises(Exception):
            Demand(5, 1)

    def test_downward_sloping_supply_raises(self):
        with self.assertRaises(Exception):
            Supply(0, -1)

    def test_blind_sum_rejects_elastic(self):
        elastic = AffineElement(5, 0)  # perfectly elastic
        with self.assertRaises(Exception):
            blind_sum(elastic)

    def test_horizontal_sum_rejects_inelastic(self):
        inelastic = AffineElement(5, 0, inverse=False)  # perfectly inelastic
        with self.assertRaises(Exception):
            horizontal_sum(inelastic)

    def test_upward_sloping_ppf_raises(self):
        with self.assertRaises(PPFError):
            PPF(10, 1)


class TestPPF(unittest.TestCase):

    def setUp(self):
        self.ppf = PPF(10, -1)

    def test_call(self):
        self.assertAlmostEqual(self.ppf(5), 5)
        self.assertTrue(np.isnan(self.ppf(12)))

    def test_shifts_return_type(self):
        shifted = self.ppf.horizontal_shift(2, inplace=False)
        self.assertIsInstance(shifted, PPF)
        shifted_v = self.ppf.vertical_shift(1, inplace=False)
        self.assertIsInstance(shifted_v, PPF)

    def test_scalar_multiplication(self):
        scaled = 2 * self.ppf
        self.assertIsInstance(scaled, PPF)
        self.assertEqual(scaled.intercept, [2 * self.ppf.intercept[0]])
        self.assertEqual(scaled.slope, self.ppf.slope)
        self.assertAlmostEqual(scaled.q_intercept, 2 * self.ppf.q_intercept)

    def test_addition(self):
        other = PPF(5, -0.5)
        joint = self.ppf + other
        # addition should produce a new PPF instance
        self.assertIsInstance(joint, PPF)
        # verify calling on key points
        self.assertAlmostEqual(joint(0), 15.0)
        self.assertAlmostEqual(joint(10), 10.0)
        self.assertAlmostEqual(joint(20), 0.0)

    def test_commutative_add(self):
        p1 = PPF(10, -1)
        p2 = PPF(5, -0.5)
        self.assertAlmostEqual((p1 + p2)(7), (p2 + p1)(7))

