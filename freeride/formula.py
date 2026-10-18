"""Parse the small affine and quadratic formulas used by FreeRide."""

import ast
import math
import re

from freeride.exceptions import FormulaParseError


def _equation_sides(equation):
    """Normalize notation without discarding any part of the equation."""
    if not isinstance(equation, str):
        raise FormulaParseError("Equation must be a string")
    if "/" in equation:
        raise FormulaParseError(
            "Unexpected character '/'. Use decimals and not fractions."
        )
    equation = equation.lower().translate(str.maketrans({"p": "y", "q": "x"}))
    if not re.fullmatch(r"[0-9xy+\-*().^²=\s]+", equation):
        raise FormulaParseError("Invalid characters in equation")
    if equation.count("=") != 1:
        raise FormulaParseError("Equation must contain exactly one '=' sign")

    equation = re.sub(r"\s+", " ", equation)
    equation = equation.replace("^", "**").replace("²", "**2")
    # A coefficient may be written as 2x, 2*x, x2, or x*2.
    equation = re.sub(r"(?<=[0-9.])\s*(?=[xy])", "*", equation)
    equation = re.sub(r"(?<=[xy])\s*(?=[0-9.])", "*", equation)
    return tuple(side.strip() for side in equation.split("="))


def _polynomial_coefficients(expression, max_degree, variables):
    """Read coefficients directly; keys are the powers of x and y."""
    def multiply(left, right):
        product = {}
        for (lx, ly), a in left.items():
            for (rx, ry), b in right.items():
                if a == 0 or b == 0:
                    continue
                powers = (lx + rx, ly + ry)
                if sum(powers) > max_degree:
                    raise FormulaParseError(
                        f"Equation must have degree at most {max_degree}"
                    )
                product[powers] = product.get(powers, 0.0) + a * b
        return product

    def coefficients(node):
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            try:
                result = {(0, 0): float(node.value)}
            except OverflowError as exc:
                raise FormulaParseError("Coefficients must be finite") from exc
        elif isinstance(node, ast.Name) and node.id in variables:
            result = {(1, 0) if node.id == "x" else (0, 1): 1.0}
        elif isinstance(node, ast.UnaryOp) and isinstance(
            node.op, (ast.UAdd, ast.USub)
        ):
            sign = -1 if isinstance(node.op, ast.USub) else 1
            result = {
                powers: sign * value
                for powers, value in coefficients(node.operand).items()
            }
        elif isinstance(node, ast.BinOp):
            left = coefficients(node.left)
            if isinstance(node.op, ast.Pow):
                exponent = node.right
                if (
                    not isinstance(exponent, ast.Constant)
                    or type(exponent.value) is not int
                    or not 0 <= exponent.value <= max_degree
                ):
                    raise FormulaParseError(
                        f"Powers must be whole numbers from 0 to {max_degree}"
                    )
                result = {(0, 0): 1.0}
                for _ in range(exponent.value):
                    result = multiply(result, left)
            else:
                right = coefficients(node.right)
                if isinstance(node.op, ast.Mult):
                    result = multiply(left, right)
                elif isinstance(node.op, (ast.Add, ast.Sub)):
                    sign = -1 if isinstance(node.op, ast.Sub) else 1
                    result = left.copy()
                    for powers, value in right.items():
                        result[powers] = result.get(powers, 0.0) + sign * value
                else:
                    raise FormulaParseError("Invalid operation in equation")
        else:
            raise FormulaParseError("Invalid syntax or variable in equation")
        if not all(math.isfinite(value) for value in result.values()):
            raise FormulaParseError("Coefficients must be finite")
        return result

    try:
        tree = ast.parse(expression, mode="eval")
    except (SyntaxError, ValueError) as exc:
        raise FormulaParseError("Invalid syntax in equation") from exc
    return coefficients(tree.body)


def _formula(equation: str):
    """Return ``(intercept, slope)`` for an affine equation.

    Accepts ``y = mx + b``, ``x = my + b``, and implicit equations such as
    ``2x + 3y = 6``. Variables may also be ``p``/``q`` in either case.
    Coefficients may use optional multiplication signs, and parentheses,
    addition, subtraction, and multiplication by constants are supported.
    The equation must define y as a function of x. Fractions, nonlinear
    terms, and nonfinite coefficients raise :class:`FormulaParseError`.

    Examples
    --------
    >>> _formula('y = 10 - 2x')
    (10.0, -2.0)
    >>> _formula('y = 10 - x*2')
    (10.0, -2.0)
    >>> _formula('2x + 3y = 6')
    (2.0, -0.6666666666666666)
    """
    left, right = _equation_sides(equation)
    terms = _polynomial_coefficients(f"({left}) - ({right})", 1, {"x", "y"})
    y_coefficient = terms.get((0, 1), 0.0)
    if y_coefficient == 0:
        raise FormulaParseError("Equation does not define y as a function of x")
    intercept = -terms.get((0, 0), 0.0) / y_coefficient
    slope = -terms.get((1, 0), 0.0) / y_coefficient
    if not all(math.isfinite(value) for value in (intercept, slope)):
        raise FormulaParseError("Coefficients must be finite")
    return float(intercept), float(slope)


def _quadratic_formula(equation: str):
    """Return ``(a, b, c)`` for ``y = ax² + bx + c``.

    Accepts the reversed equation ``ax² + bx + c = y``, optional ``*`` in
    coefficients, and the square notations ``x^2``, ``x**2``, and ``x²``.
    Variables may also be ``p``/``q`` in either case. Repeated terms are
    added together. Fractions, unknown syntax, and terms above degree two
    raise :class:`FormulaParseError`.

    Examples
    --------
    >>> _quadratic_formula('y = 2x^2 + 3x - 1')
    (2.0, 3.0, -1.0)
    >>> _quadratic_formula('P = -0.5Q**2 + 2Q + 4')
    (-0.5, 2.0, 4.0)
    >>> _quadratic_formula('y = -x² + 1')
    (-1.0, 0.0, 1.0)
    """
    left, right = _equation_sides(equation)
    if left == "y":
        expression = right
    elif right == "y":
        expression = left
    else:
        raise FormulaParseError(
            "Equation must be in the form 'y = ...' or '... = y'"
        )
    terms = _polynomial_coefficients(expression, 2, {"x"})
    return tuple(terms.get(powers, 0.0) for powers in ((2, 0), (1, 0), (0, 0)))
