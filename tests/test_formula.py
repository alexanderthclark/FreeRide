import unittest
from freeride.formula import _formula, _quadratic_formula

class TestFormula(unittest.TestCase):

    def setUp(self):
        s1 = 'P = 10 - 2*Q'
        s2 = 'P = 10 - 2Q'
        s3 = 'p = 2 + 4*q'
        s4 = 'y = 1*x'
        s5 = 'x = 2y'
        s6 = 'y=x'

        self.affine1 = _formula(s1)
        self.affine2 = _formula(s2)
        self.affine3 = _formula(s3)
        self.affine4 = _formula(s4)
        self.affine5 = _formula(s5)
        self.affine6 = _formula(s6)

    def test_coef(self):

        self.assertTrue(self.affine1[1] == self.affine2[1] == -2)
        self.assertTrue(self.affine3[1] == 4)
        self.assertTrue(self.affine4[0] == 0)
        self.assertTrue(self.affine4[1] == 1)
        self.assertTrue(self.affine5[0] == 0)
        self.assertTrue(self.affine5[1] == 0.5)
        self.assertTrue(self.affine6[0] == 0)
        self.assertTrue(self.affine6[1] == 1)

    def tearDown(self):
        pass

class TestQuadraticParser(unittest.TestCase):

    def setUp(self):
        pass

    def test_standard_form(self):
        self.assertEqual(_quadratic_formula('y = 2x^2 + 3x - 1'), (2.0, 3.0, -1.0))

    def test_with_p_and_q(self):
        self.assertEqual(_quadratic_formula('P = -0.5Q^2 + 2Q + 4'), (-0.5, 2.0, 4.0))

    def test_missing_constant(self):
        self.assertEqual(_quadratic_formula('y = x^2 - x'), (1.0, -1.0, 0.0))

    def test_reversed_order(self):
        self.assertEqual(_quadratic_formula('2x^2 - 4x + 2 = y'), (2.0, -4.0, 2.0))

    def test_negative_x_squared(self):
        self.assertEqual(_quadratic_formula('y = -x^2 + 1'), (-1.0, 0.0, 1.0))

    def test_decimal_coefficients(self):
        self.assertEqual(_quadratic_formula('y = 1.5x^2 - 2.7x + 3.14'), (1.5, -2.7, 3.14))

    def test_missing_x_term(self):
        self.assertEqual(_quadratic_formula('y = 3x^2 + 2'), (3.0, 0.0, 2.0))

    def test_missing_constant_term(self):
        self.assertEqual(_quadratic_formula('y = 2x^2 - 4x'), (2.0, -4.0, 0.0))

    def test_only_x_squared(self):
        self.assertEqual(_quadratic_formula('y = x^2'), (1.0, 0.0, 0.0))

    def test_coefficients_different_order(self):
        self.assertEqual(_quadratic_formula('y = 1 - 3x + 2x^2'), (2.0, -3.0, 1.0))

    def test_all_negative_terms(self):
        self.assertEqual(_quadratic_formula('y = -2x^2 - 3x - 4'), (-2.0, -3.0, -4.0))

    def test_x_on_left_side(self):
        self.assertEqual(_quadratic_formula('3x^2 + 2x - 1 = y'), (3.0, 2.0, -1.0))

    def test_implicit_one_coefficient(self):
        self.assertEqual(_quadratic_formula('y = 2x^2 + x - 3'), (2.0, 1.0, -3.0))

    def test_large_coefficients(self):
        self.assertEqual(_quadratic_formula('y = 100x^2 - 200x + 300'), (100.0, -200.0, 300.0))

    def test_no_spaces(self):
        self.assertEqual(_quadratic_formula('y=0.5x^2-0.25x+0.125'), (0.5, -0.25, 0.125))

    def tearDown(self):
        pass
