'''
Formula module using sympy
'''
import re
from microecon.curves import Affine


def formula(equation: str):
    """
    Parse a linear equation string and return an Affine object.

    This function supports linear equations in formats like 'y = mx + b', 
    'y = b + mx', 'x = my + b', and 'x = b + my', with optional whitespaces 
    and signs for coefficients. The variables 'y' and 'x' can also be 
    represented as 'p', 'P', 'q', or 'Q', respectively.

    Parameters
    ----------
    equation : str
        A string representing a linear equation.

    Returns
    -------
    Affine
        An object containing the intercept and slope extracted from the equation.

    Raises
    ------
    ValueError
        If the input string is not in a valid equation format or if there is 
        a fraction instead of decimal coefficients or a zero slope.

    Examples
    --------
    >>> formula('y = 10 - 2x')
    Affine(intercept=10.0, slope=-2.0)
    >>> formula('y = 10 - 2*x')
    Affine(intercept=10.0, slope=-2.0)
    >>> formula('P=3+0.5Q')
    Affine(intercept=3.0, slope=0.5)

    """
    # Remove whitespaces and equate p with y and q with x
    equation = (equation.lower()
                       .replace("p", "y")
                       .replace("q", "x")
                       .replace(" ", ""))

    if '/' in equation:
    	raise ValueError("Unexpected character '/'. Use decimals and not fractions.")
    
    # Check if equation is in form of y = mx + b or y = b + mx
    match = re.match(r"y=(-?\d*\.?\d*)\*?x([+-]\d+\.?\d*)?|y=([+-]?\d+\.?\d*)([+-]\d*\.?\d*)\*?x", equation)
    if match:
        slope = float(match.group(1) or match.group(4) or '1')  # Default slope is 1 if not specified
        intercept = float(match.group(2) or match.group(3) or '0')  # Default intercept is 0 if not specified
        return Affine(intercept, slope)

    # Check if equation is in form of x = my + b or x = b + my
    match = re.match(r"x=(-?\d*\.?\d*)\*?y([+-]\d+\.?\d*)?|x=([+-]?\d+\.?\d*)([+-]\d*\.?\d*)\*?y", equation)
    if match:
        slope = float(match.group(1) or match.group(4) or '1')  # Default slope is 1 if not specified
        intercept = float(match.group(2) or match.group(3) or '0')  # Default intercept is 0 if not specified
        return Affine(intercept, 1 / slope)  # Inverting the slope for this case

    raise ValueError("Invalid equation")
