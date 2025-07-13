import unittest
from freeride.quadratic import QuadraticElement

class TestQuadraticElementVerticalShift(unittest.TestCase):
    def test_vertical_shift_inplace(self):
        q = QuadraticElement(1, 2, 3)
        q.vertical_shift(4, inplace=True)
        self.assertEqual(q.intercept, 5)
        self.assertEqual(q.linear_coef, 2)
        self.assertEqual(q.quadratic_coef, 3)
        self.assertEqual(q(0), 5)

    def test_vertical_shift_new_instance(self):
        q = QuadraticElement(1, 2, 3)
        shifted = q.vertical_shift(-1, inplace=False)
        self.assertIsInstance(shifted, QuadraticElement)
        self.assertEqual(shifted.intercept, 0)
        self.assertEqual(shifted.linear_coef, 2)
        self.assertEqual(shifted.quadratic_coef, 3)
        # original should remain unchanged
        self.assertEqual(q.intercept, 1)
        self.assertEqual(q(0), 1)
