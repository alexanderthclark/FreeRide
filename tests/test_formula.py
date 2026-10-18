import ast
import unittest
from unittest.mock import patch
from freeride.formula import _formula, _quadratic_formula
from freeride.exceptions import FormulaParseError
from freeride.quadratic import QuadraticElement

class TestFormula(unittest.TestCase):

    def setUp(self):
        s1 = 'P = 10 - 2*Q'
        s2 = 'P = 10 - 2Q'
        s3 = 'p = 2 + 4*q'
        s4 = 'y = 1*x'
        s5 = 'x = 2y'
        s6 = 'y=x'
        s7 = 'y = 10 - x'
        s8 = 'y = 10 - x*2'
        s9 = 'x + y = 10'
        s10 = '2x + 3y = 6'

        self.affine1 = _formula(s1)
        self.affine2 = _formula(s2)
        self.affine3 = _formula(s3)
        self.affine4 = _formula(s4)
        self.affine5 = _formula(s5)
        self.affine6 = _formula(s6)
        self.affine7 = _formula(s7)
        self.affine8 = _formula(s8)
        self.affine9 = _formula(s9)
        self.affine10 = _formula(s10)

    def test_coef(self):
        """Verify both slope and intercept parsing for a variety of forms."""

        # Slopes
        self.assertEqual(self.affine1[1], -2)
        self.assertEqual(self.affine2[1], -2)
        self.assertEqual(self.affine3[1], 4)
        self.assertEqual(self.affine4[1], 1)
        self.assertEqual(self.affine5[1], 0.5)
        self.assertEqual(self.affine6[1], 1)
        self.assertEqual(self.affine7[1], -1)
        self.assertEqual(self.affine8[1], -2)
        self.assertEqual(self.affine9[1], -1)
        self.assertAlmostEqual(self.affine10[1], -2/3)

        # Intercepts
        self.assertEqual(self.affine1[0], 10)
        self.assertEqual(self.affine2[0], 10)
        self.assertEqual(self.affine3[0], 2)
        self.assertEqual(self.affine4[0], 0)
        self.assertEqual(self.affine5[0], 0)
        self.assertEqual(self.affine6[0], 0)
        self.assertEqual(self.affine7[0], 10)
        self.assertEqual(self.affine8[0], 10)
        self.assertEqual(self.affine9[0], 10)
        self.assertEqual(self.affine10[0], 2)

    def test_fraction_raises(self):
        """Fractions are not supported and should raise a FormulaParseError."""
        with self.assertRaises(FormulaParseError):
            _formula("y = 1/2x + 3")

    def test_invalid_equation_raises(self):
        """Equations that do not match the expected forms should error."""
        with self.assertRaises(FormulaParseError):
            _formula("y = x*y")

    def test_numeric_literals_without_legacy_ast_num(self):
        """Numeric literals parse when the deprecated ``ast.Num`` is absent."""
        legacy_num = ast.__dict__.pop("Num", None)
        original_getattr = getattr(ast, "__getattr__", None)

        def without_num(name):
            if name == "Num" or original_getattr is None:
                raise AttributeError(name)
            return original_getattr(name)

        try:
            with patch.object(ast, "__getattr__", without_num, create=True):
                self.assertFalse(hasattr(ast, "Num"))
                self.assertEqual(_formula("y = 3 + 2*x"), (3.0, 2.0))
                self.assertEqual(_quadratic_formula("y = 2*x**2 + 3"), (2.0, 0.0, 3.0))
        finally:
            if legacy_num is not None:
                ast.Num = legacy_num

    def test_equivalent_affine_forms(self):
        for equation in (
            "P = 10 - 2Q", "10 - Q*2 = P", "P + 2Q = 10",
            "2P + 4Q = 20", "Q = 5 - 0.5P",
            "P = 2*(5 - Q)", "P = 10 - Q - Q",
        ):
            with self.subTest(equation=equation):
                self.assertEqual(_formula(equation), (10.0, -2.0))

    def test_hidden_nonlinear_terms_are_rejected(self):
        for equation in (
            "y = (x+1)*(x+2)", "y = x**2", "y = x^2",
            "x*(y+1) = 2", "y = (x*x) + 1", "x*x + y = 3",
        ):
            with self.subTest(equation=equation):
                with self.assertRaises(FormulaParseError):
                    _formula(equation)

    def test_large_intercept_does_not_erase_the_slope(self):
        self.assertEqual(_formula("y = 10000000000000000 + x"), (1e16, 1.0))

    def test_malformed_affine_equations_are_rejected(self):
        for equation in (
            "y = x + garbage", "y = x; 2", "y = x(2)",
            "y = x//2", "y = x[0]", "y = x = 2", "y =",
            "x = 2", "y = 1 0 + x", "y = 2(x+1)",
        ):
            with self.subTest(equation=equation):
                with self.assertRaises(FormulaParseError):
                    _formula(equation)

    def test_nonfinite_coefficients_are_rejected(self):
        huge_decimal = "9" * 400 + ".0"
        expressions = (
            huge_decimal,
            "9" * 400,
            "(" + "9" * 200 + ".0)*" + "9" * 200 + ".0",
            "nan",
            "inf",
        )
        for parser in (_formula, _quadratic_formula):
            for expression in expressions:
                with self.subTest(parser=parser.__name__, expression=expression):
                    with self.assertRaises(FormulaParseError):
                        parser("y = " + expression + " + x")

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

    def test_fraction_raises(self):
        """Fractions should trigger a FormulaParseError."""
        with self.assertRaises(FormulaParseError):
            _quadratic_formula('y = 1/2x^2 + x + 1')

    def test_missing_y_side_raises(self):
        """Equations without '= y' should error."""
        with self.assertRaises(FormulaParseError):
            _quadratic_formula('x^2 + x + 1')

    def test_multiple_equals_raises(self):
        """Equations with extra '=' signs should error."""
        with self.assertRaises(FormulaParseError):
            _quadratic_formula('y = x^2 + x + 1 = z')

    def test_equivalent_square_and_coefficient_forms(self):
        for equation in (
            "y = 2x^2 + 3x + 4", "y = 2*x**2 + 3*x + 4",
            "4 + x*3 + x²*2 = y", "P = 2Q² + 3Q + 4",
            "y = x² + x² + x + 2x + 4", "y = 2*(x*x) + 3*x + 4",
        ):
            with self.subTest(equation=equation):
                self.assertEqual(_quadratic_formula(equation), (2.0, 3.0, 4.0))

    def test_formula_builds_the_requested_quadratic(self):
        curve = QuadraticElement.from_formula("y = 2*x**2 + 3*x + 4")
        self.assertEqual(curve(2), 18)

    def test_parenthesized_polynomial_keeps_its_coefficients(self):
        self.assertEqual(_quadratic_formula("y = (x+1)*(x+2)"), (1.0, 3.0, 2.0))

    def test_unmatched_or_nonlinear_syntax_is_rejected(self):
        for equation in (
            "y = x^2 + garbage", "y = x^2 + 3x + 1junk",
            "y = x^3 + 2", "y = x**4", "y = x*x*x", "y = x**2*y",
            "y = x² + y", "y = x**2 + 1/2", "y = x^2; 3",
            "y = x^2 +", "y = x**-2", "y = x**0.5", "y = x(2)",
            "y = x**2 + 1 0", "2y = x**2", "y = 2(x**2)",
        ):
            with self.subTest(equation=equation):
                with self.assertRaises(FormulaParseError):
                    _quadratic_formula(equation)

    def tearDown(self):
        pass
