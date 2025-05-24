"""
Formula module using sympy
"""

import re

from freeride.exceptions import FormulaParseError


def _formula(equation: str):
    """
    Parse a linear equation string and return an Affine object.

    Accepts equations in forms like 'y = mx + b', 'y = b + mx',
    'x = my + b', and 'x = b + my'. Variables 'y' and 'x' can be
    'p', 'P', 'q', or 'Q'. Handles optional whitespaces, signs for
    coefficients, and decimal coefficients.

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
        If the equation is not valid, contains fractions, or has a zero slope.

    Examples
    --------
    >>> _formula('y = 10 - 2x')
    (10.0, -2.0)
    >>> _formula('y = 10 - 2*x')
    (10.0, -2.0)
    >>> _formula('P=3+0.5Q')
    (3.0, 0.5)
    """
    # Remove whitespaces and equate p with y and q with x
    equation = (
        equation.lower().replace("p", "y").replace("q", "x").replace(" ", "")
    )

    if "/" in equation:
        raise FormulaParseError(
            "Unexpected character '/'. Use decimals and not fractions."
        )

    # Check if equation is in form of y = mx + b or y = b + mx
    pattern_y = (
        r"y=([-+]?\d*\.?\d*)\*?x([-+]\d*\.?\d*)?"
        r"|y=([-+]?\d*\.?\d*)([-+]\d*\.?\d*)\*?x?"
    )
    match = re.match(pattern_y, equation)
    if match:
        if match.group(1) is not None and match.group(1) != "":
            slope = float(match.group(1) if match.group(1) != "-" else -1)
            intercept = float(
                match.group(2)
                if match.group(2) not in (None, "", "+", "-")
                else "0"
            )
        else:
            slope = float(
                match.group(4)
                if match.group(4) not in (None, "", "+", "-")
                else "1"
            )
            intercept = float(
                match.group(3)
                if match.group(3) not in (None, "", "+", "-")
                else "0"
            )
        return intercept, slope

    # Check if equation is in form of x = my + b or x = b + my
    pattern_x = (
        r"x=([-+]?\d*\.?\d*)\*?y([-+]\d*\.?\d*)?"
        r"|x=([-+]?\d*\.?\d*)([-+]\d*\.?\d*)\*?y?"
    )
    match = re.match(pattern_x, equation)
    if match:
        if match.group(1) is not None and match.group(1) != "":
            slope = float(match.group(1) if match.group(1) != "-" else -1)
            intercept = float(
                match.group(2)
                if match.group(2) not in (None, "", "+", "-")
                else "0"
            )
        else:
            slope = float(
                match.group(4)
                if match.group(4) not in (None, "", "+", "-")
                else "1"
            )
            intercept = float(
                match.group(3)
                if match.group(3) not in (None, "", "+", "-")
                else "0"
            )
        return -intercept / slope, 1 / slope

    raise FormulaParseError("Invalid equation")


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
    terms = re.findall(
        (r"([+-]?(?:\d*\.)?\d*x²|[+-]?(?:\d*\.)?\d*x|" r"[+-]?(?:\d*\.)?\d+)"),
        left_side,
    )

    a, b, c = 0, 0, 0

    for term in terms:
        if "x²" in term:
            coef = term.replace("x²", "")
            a = (
                float(coef)
                if coef and coef not in ("+", "-")
                else (1 if coef in ("", "+") else -1)
            )
        elif "x" in term:
            coef = term.replace("x", "")
            b = (
                float(coef)
                if coef and coef not in ("+", "-")
                else (1 if coef in ("", "+") else -1)
            )
        elif term:
            c += float(term)

    return a, b, c
