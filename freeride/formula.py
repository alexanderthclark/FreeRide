'''
Formula module using sympy
'''
import re

def _formula(equation: str):
    """
    Parse a linear equation string and return an Affine object.

    Accepts equations in forms like 'y = mx + b', 'y = b + mx', 'x = my + b', 
    and 'x = b + my'. Variables 'y' and 'x' can be 'p', 'P', 'q', or 'Q'. 
    Handles optional whitespaces, signs for coefficients, and decimal coefficients.

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
    ValueError
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
    equation = (equation.lower()
                       .replace("p", "y")
                       .replace("q", "x")
                       .replace(" ", ""))

    if '/' in equation:
        raise ValueError("Unexpected character '/'. Use decimals and not fractions.")
    
    # Check if equation is in form of y = mx + b or y = b + mx
    match = re.match(r"y=([-+]?\d*\.?\d*)\*?x([-+]\d*\.?\d*)?|y=([-+]?\d*\.?\d*)([-+]\d*\.?\d*)\*?x?", equation)
    if match:
        if match.group(1) is not None and match.group(1) != '':
            slope = float(match.group(1) if match.group(1) != '-' else -1)
            intercept = float(match.group(2) if match.group(2) not in (None, '', '+', '-') else '0')
        else:
            slope = float(match.group(4) if match.group(4) not in (None, '', '+', '-') else '1')
            intercept = float(match.group(3) if match.group(3) not in (None, '', '+', '-') else '0')
        return intercept, slope

    # Check if equation is in form of x = my + b or x = b + my
    match = re.match(r"x=([-+]?\d*\.?\d*)\*?y([-+]\d*\.?\d*)?|x=([-+]?\d*\.?\d*)([-+]\d*\.?\d*)\*?y?", equation)
    if match:
        if match.group(1) is not None and match.group(1) != '':
            slope = float(match.group(1) if match.group(1) != '-' else -1)
            intercept = float(match.group(2) if match.group(2) not in (None, '', '+', '-') else '0')
        else:
            slope = float(match.group(4) if match.group(4) not in (None, '', '+', '-') else '1')
            intercept = float(match.group(3) if match.group(3) not in (None, '', '+', '-') else '0')
        return -intercept / slope, 1 / slope
    
    raise ValueError("Invalid equation")
