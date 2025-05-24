import unittest
from freeride.curves import Affine, BaseAffine, Demand

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
