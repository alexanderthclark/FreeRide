"""Parse linear and quadratic formula strings."""

import ast
import operator
import re

from freeride.exceptions import FormulaParseError

_ALLOWED_BINARY_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
}


def _eval_ast_node(node, allowed_names, values):
    """Recursively evaluate an AST node with restricted operations."""
    if isinstance(node, ast.Expression):
        result = _eval_ast_node(node.body, allowed_names, values)
    elif isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_BINARY_OPERATORS:
        left = _eval_ast_node(node.left, allowed_names, values)
        right = _eval_ast_node(node.right, allowed_names, values)
        result = _ALLOWED_BINARY_OPERATORS[type(node.op)](left, right)
    elif isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        operand = _eval_ast_node(node.operand, allowed_names, values)
        result = operand if isinstance(node.op, ast.UAdd) else -operand
    elif isinstance(node, ast.Num):  # Python <3.8 compatibility
        result = node.n
    elif isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        result = node.value
    elif isinstance(node, ast.Name):
        if node.id not in allowed_names:
            raise FormulaParseError(f"Invalid variable '{node.id}' in equation")
        result = values.get(node.id, 0.0)
    else:
        raise FormulaParseError("Invalid syntax in equation")

    return result


def _formula(equation: str):
    """
    Parse a linear equation string and return an Affine object.

    Accepts linear equations in a variety of notations including
    ``y = mx + b``, ``x = my + b`` and the implicit form
    ``ax + by = c``. Coefficients may appear with or without an
    explicit ``*`` (e.g. ``2x`` or ``2*x``) and variables may also be
    written as ``p``/``q``.  Whitespaces are ignored.

    Parameters
    ----------
    equation : str
        A string representing a linear equation.

    Returns
    -------
    tuple
        A tuple (intercept, slope) derived from the equation.

    Raises
    ------
    FormulaParseError
        If the equation is not valid or contains fractions.

    Examples
    --------
    >>> _formula('y = 10 - 2x')
    (10.0, -2.0)
    >>> _formula('y = 10 - 2*x')
    (10.0, -2.0)
    >>> _formula('P=3+0.5Q')
    (3.0, 0.5)
    """
    # Normalize string: remove whitespace, convert to lowercase and unify
    # variable names so both ``p``/``q`` and ``y``/``x`` are accepted.
    equation = (
        equation.lower().replace("p", "y").replace("q", "x").replace(" ", "")
    )

    if "/" in equation:
        raise FormulaParseError(
            "Unexpected character '/'. Use decimals and not fractions."
        )

    # Insert missing multiplication symbols so ``2x`` becomes ``2*x`` and
    # ``x*2`` becomes ``2*x`` for easier evaluation.
    equation = re.sub(r"(?<=\d)(?=[xy])", "*", equation)
    equation = re.sub(r"([xy])(?=\d)", r"\1*", equation)
    equation = re.sub(r"([xy])\*([-+]?\d*\.?\d+)", r"\2*\1", equation)

    if any(t in equation for t in ("x*y", "y*x", "x*x", "y*y", "**")):
        raise FormulaParseError("Equation must be affine")

    if equation.count("=") != 1:
        raise FormulaParseError("Equation must contain exactly one '=' sign")

    lhs, rhs = equation.split("=")

    def _safe_eval(expr: str, **values: float) -> float:
        """Safely evaluate arithmetic expressions for x and y."""
        if not re.fullmatch(r"[0-9xy+\-*.()]+", expr):
            raise FormulaParseError("Invalid characters in equation")

        try:
            ast_tree = ast.parse(expr, mode="eval")
        except SyntaxError as exc:
            raise FormulaParseError("Invalid syntax in equation") from exc

        allowed_names = {"x", "y"}
        result = _eval_ast_node(ast_tree, allowed_names, values)
        return float(result)

    # If equation is given explicitly as y = f(x)
    if lhs == "y" or rhs == "y":
        expr = rhs if lhs == "y" else lhs
        if "y" in expr:
            raise FormulaParseError("y must be expressed solely in terms of x")
        intercept = _safe_eval(expr, x=0, y=0)
        y_at_one = _safe_eval(expr, x=1, y=0)
        slope = y_at_one - intercept
        return float(intercept), float(slope)

    # x = f(y)
    if lhs == "x" or rhs == "x":
        expr = rhs if lhs == "x" else lhs
        if "x" in expr:
            raise FormulaParseError("x must be expressed solely in terms of y")
        x_intercept_at_zero = _safe_eval(expr, x=0, y=0)
        x_at_one = _safe_eval(expr, x=0, y=1)
        inverse_slope = x_at_one - x_intercept_at_zero
        if inverse_slope == 0:
            raise FormulaParseError("Zero slope invalid for x=f(y)")
        intercept = -x_intercept_at_zero / inverse_slope
        slope = 1 / inverse_slope
        return float(intercept), float(slope)

    # General form ax + by = c
    expr = f"{lhs}-({rhs})"
    base = _safe_eval(expr, x=0, y=0)
    x_coefficient = _safe_eval(expr, x=1, y=0) - base
    y_coefficient = _safe_eval(expr, x=0, y=1) - base
    constant = -base
    if y_coefficient == 0:
        raise FormulaParseError("Equation does not define y as a function of x")
    intercept = constant / y_coefficient
    slope = -x_coefficient / y_coefficient
    return float(intercept), float(slope)


def _quadratic_formula(equation: str):
    """
    Parse a quadratic equation string and return the coefficients a, b, and c.
    Accepts equations in the form 'y = ax^2 + bx + c' or 'ax^2 + bx + c = y'.
    Variables 'y' and 'x' can be 'p', 'P', 'q', or 'Q'. Handles optional
    whitespaces, signs for coefficients, and decimal coefficients.

    Parameters
    ----------
    equation : str
        A string representing a quadratic equation.

    Returns
    -------
    tuple
        A tuple (a, b, c) representing the coefficients of the
        quadratic equation.

    Raises
    ------
    FormulaParseError
        If the equation is not a valid quadratic equation or
        contains fractions.

    Examples
    --------
    >>> _quadratic_formula('y = 2x^2 + 3x - 1')
    (2.0, 3.0, -1.0)
    >>> _quadratic_formula('P = -0.5Q^2 + 2Q + 4')
    (-0.5, 2.0, 4.0)
    >>> _quadratic_formula('y = -x^2 + 1')
    (-1.0, 0.0, 1.0)
    """
    # Remove whitespaces and equate p with y and q with x
    equation = (
        equation.lower()
        .replace("p", "y")
        .replace("q", "x")
        .replace(" ", "")
        .replace("^2", "²")
        .replace("**2", "²")
    )  # Replace ^2 with ² for easier parsing

    if "/" in equation:
        raise FormulaParseError(
            "Unexpected character '/'. Use decimals and not fractions."
        )

    # Ensure the equation is in the form ax²+bx+c=y
    if "y=" in equation:
        equation = equation.replace("y=", "") + "=y"

    # Split the equation into left and right sides
    try:
        left_side, right_side = equation.split("=")
    except ValueError as exc:
        raise FormulaParseError(
            "Equation must contain exactly one '=' sign"
        ) from exc

    if right_side != "y":
        raise FormulaParseError(
            "Equation must be in the form 'y = ...' or '... = y'"
        )

    # Use regex to find terms
    term_pattern = r"[+-]?(?:\d*\.)?\d*x²|[+-]?(?:\d*\.)?\d*x|[+-]?(?:\d*\.)?\d+"
    terms = re.findall(term_pattern, left_side)

    quadratic_coef = 0.0
    linear_coef = 0.0
    constant = 0.0

    for term in terms:
        if "x²" in term:
            coef = term.replace("x²", "")
            quadratic_coef = (
                float(coef)
                if coef and coef not in ("+", "-")
                else (1 if coef in ("", "+") else -1)
            )
        elif "x" in term:
            coef = term.replace("x", "")
            linear_coef = (
                float(coef)
                if coef and coef not in ("+", "-")
                else (1 if coef in ("", "+") else -1)
            )
        elif term:
            constant += float(term)

    return quadratic_coef, linear_coef, constant
