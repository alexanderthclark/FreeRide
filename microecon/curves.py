import numpy as np
import matplotlib.pyplot as plt
import numbers
from microecon.plotting import textbook_axes


class PolyBase(np.polynomial.Polynomial):
    """
    A base class for polynomial functions with added methods.
    The independent variable is q instead of x to align with typical price-quantity axes.
    The dependent variable is is explicitly named as p instead of y.

    This class extends NumPy's polynomial class and provides additional methods for
    working with polynomial functions.

    .. math::

       p = \\sum_{k=0}^n c_k q^k

    Parameters
    ----------
    *coef : array-like or scalar
        Coefficients of the polynomial. Can be specified as a list, tuple, or individual numerical arguments.

    Attributes
    ----------
        coef (ndarray): Coefficients of the polynomial.

    Example:
        To create a polynomial and use its methods:

        >>> poly = PolyBase([1, -2, 1])  # Represents x^2 - 2x + 1
        >>> poly.p(2.0)  # Calculate the price at q=2.0
        1.0
    """
    def __init__(self, *coef, symbol='q'):
        """
        Initialize a PolyBase object with the given coefficients.
        The coefficients determine the polynomial represented by the object.

        Parameters
        ----------
        *coef : array-like or scalar
            Coefficients of the polynomial. Can be specified as a list, tuple, or individual numerical arguments.

        Returns
        ----------
            None

        Examples
        --------
            >>> poly = PolyBase([1, -2, 3])  # Represents 1 - 2q + 3q^2
            >>> poly = PolyBase(1, -2, 3)  # Equivalent to the above
        """
        self.is_undefined = coef == ([],)  # helpful in sum functions
        if self.is_undefined == False:
            coef = np.squeeze(np.array(coef, ndmin=1))
            super().__init__(coef, symbol=symbol)
        else:
            self.coef = []
            self._symbol = 'q'
    def __call__(self, x):
        if self.is_undefined:
            raise ValueError("Polynomial is undefined.")
        else:
            return super().__call__(x)

    def p(self, q: float):
        """
        Calculate the price given a quantity value q.

        Parameters
        --------
            q (float): The quantity value.

        Returns
        --------
            float: The corresponding price.

        Example
        --------
            >>> poly = PolyBase([1, -2, 3])  # Represents 1 - 2x + 3x^2
            >>> poly.p(2.0)
            9.0
        """
        return self.__call__(q)

    def q(self, p):
        """
        Calculate the quantity given a price value p.

        Parameters
        --------
            p (float): The price value.

        Returns
        --------
            float or ndarray: The corresponding quantity or array of quantities.

        Example
        --------
            >>> poly = PolyBase([1, -2, 1])  # Represents x^2 - 2x + 1
            >>> poly.q(1.0)
            1.0
        """
        # Perfectly Inelastic
        if self.slope == np.inf:
            return self.q_intercept

        coef2 = (self.coef[0]-p, *self.coef[1:])[::-1]
        roots = np.roots(coef2)

        if roots.shape == (1,):
            return roots[0]
        else:
            return roots

    def plot(self, ax=None, label=None, max_q=100, min_plotted_q=0):
        """
        Plot the polynomial.

        Parameters
        --------
            ax (matplotlib.axes._axes.Axes, optional): The matplotlib Axes to use for plotting.
                If not provided, the current Axes will be used.
            max_q (float, optional): The maximum x-value for the plot. Defaults to 100.
            label (str, optional): The label for the plot. Defaults to None.
            min_plotted_q (float, optional): The minimum quantity value to plot.

        Returns
        --------
            None

        Example
        --------
            >>> poly = PolyBase([1, -2, 1])  # Represents x^2 - 2x + 1
            >>> poly.plot()
        """
        if ax is None:
            ax = plt.gca()

        x_vals = np.linspace(0, max_q, max_q*5 + 1)
        x_vals = x_vals[x_vals >= min_plotted_q]
        y_vals = self(x_vals)

        ax.plot(x_vals, y_vals, label = label)

        # Make textbook-style plot window
        ax.spines['left'].set_position('zero')
        ax.spines['bottom'].set_position('zero')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

    def _repr_latex_(self):
        """
        Generate LaTeX representation of the polynomial.

        Returns
        --------
            str: LaTeX representation of the polynomial.

        Example
        --------
            >>> poly = PolyBase([1, -2, 3])  # Represents 1 - 2x + 3x%2
            >>> poly._repr_latex_()
            '$p = 1 - 2q + 3q^2$'
        """
        # overwrite ABCPolyBase Method to use p/q instead of x\mapsto
        # get the scaled argument string to the basis functions
        if hasattr(self, 'is_undefined') and self.is_undefined:
            return "Undefined"
        elif hasattr(self,'inverse_expression') and self.inverse_expression != 'undefined':
            latex_str = f'p={self.inverse_expression}'
            return rf'${latex_str}$'
        elif hasattr(self, 'expression') and self.expression != 'undefined':
            latex_str = f'q={self.expression}'
            return rf"${latex_str}$"

        off, scale = self.mapparms()
        if off == 0 and scale == 1:
            term = 'q'
            needs_parens = False
        elif scale == 1:
            term = f"{self._repr_latex_scalar(off)} + q"
            needs_parens = True
        elif off == 0:
            term = f"{self._repr_latex_scalar(scale)}q"
            needs_parens = True
        else:
            term = (
                f"{self._repr_latex_scalar(off)} + "
                f"{self._repr_latex_scalar(scale)}q"
            )
            needs_parens = True

        mute = r"\color{{LightGray}}{{{}}}".format

        parts = []
        for i, c in enumerate(self.coef):
            # prevent duplication of + and - signs
            if i == 0:
                coef_str = f"{self._repr_latex_scalar(c)}"
            elif not isinstance(c, numbers.Real):
                coef_str = f" + ({self._repr_latex_scalar(c)})"
            elif not np.signbit(c):
                coef_str = f" + {self._repr_latex_scalar(c)}"
            else:
                coef_str = f" - {self._repr_latex_scalar(-c)}"

            # produce the string for the term
            term_str = self._repr_latex_term(i, term, needs_parens)
            if term_str == '1':
                part = coef_str
            else:
                part = rf"{coef_str}\,{term_str}"

            if c == 0:
                part = mute(part)

            parts.append(part)

        if parts:
            body = ''.join(parts)
        else:
            # in case somehow there are no coefficients at all
            body = '0'

        return rf"$p = {body}$"


class AffineElement(PolyBase):
    """
    This class extends the PolyBase class and represents an affine function commonly
    used in supply and demand curves. This does allow for negative quantities.

    Parameters
    --------
        intercept (float): The intercept of the affine function.
        slope (float): The slope of the affine function.
        inverse (bool, optional): If True, interprets the parameters as inverse slope
            and intercept. Defaults to True.

    Methods
    --------
        vertical_shift(delta: float):
            Shift the curve vertically by the given amount.
        horizontal_shift(delta: float):
            Shift the curve horizontally by the given amount.
        price_elasticity(p: float) -> float:
            Calculate the point price elasticity at a given price.
        midpoint_elasticity(p1: float, p2: float) -> float:
            Calculate the price elasticity between two prices using the midpoint formula.
        plot(ax=None, textbook_style=True, max_q=10, color='black', linewidth=2, label=True):
            Plot the supply or demand curve.

    Attributes
    --------
        intercept (float): The intercept of the affine function.
        slope (float): The slope of the affine function.
        q_intercept (float): The quantity intercept of the affine function.

    Example
    --------
        To create an Affine object and use its methods:

        >>> supply_curve = Affine(10.0, -2.0)
        >>> supply_curve.q(4.0)  # Calculate the quantity at price p=4.0
        6.0
    """


    def __init__(self, intercept, slope, inverse = True):
        """
        Initialize an Affine object with the given intercept and slope.

        This method creates an instance of the Affine class with the specified intercept and slope.
        The parameters can be interpreted as inverse slope and intercept if the `inverse` parameter is True.

        Parameters
        --------
            intercept (float): The intercept of the affine function.
            slope (float): The slope of the affine function.
            inverse (bool, optional): If True, interprets the parameters as inverse slope
                and intercept. Defaults to True.

        Returns
        --------
            Affine: An Affine object representing the supply or demand curve.

        Example
        --------
            >>> supply_curve = Affine(10.0, -2.0)
        """
        if slope == 0:
            if inverse:  # perfectly elastic
                self.intercept = intercept
                self.q_intercept = np.nan
                self.slope = 0

                self.inverse_expression = f'{self.intercept:g}'
                self.expression = 'undefined'
                self._symbol = 'q'  # rhs is 0*q

            else:  # perfectly inelastic
                self.q_intercept = intercept
                self.slope = np.inf
                self.intercept = np.nan

                self.inverse_expression = 'undefined'
                self.expression = f'{self.q_intercept:g}'
                self._symbol = 'p'  # rhs is 0*p
            self.coef = (self.intercept, self.slope)
            super().__init__(self.coef)
        else:
            if not inverse:
                slope, intercept = 1/slope, -intercept/slope

            coef = (intercept, slope)
            super().__init__(coef)
            self.intercept = intercept
            self.slope = slope
            self.q_intercept = -intercept/slope
            self.inverse_expression = f'{intercept:g}{slope:+g}q'
            self.expression = f'{self.q_intercept:g}{1/slope:+g}p'

    def ddcall__(self,x):
        if (self.slope == 0) or (self.slope == np.inf):
            raise 


    def vertical_shift(self, delta):
        """
        Shift the curve vertically by the given amount.

        This method shifts the supply or demand curve vertically by the specified amount `delta`.
        A positive `delta` shifts the demand curve to the right, and a negative `delta` shifts the supply curve to the left.

        Parameters
        --------
            delta (float): The amount to shift the curve vertically.

        Returns
        --------
            None

        Example
        --------
            >>> supply_curve = Affine(10.0, -2.0)
            >>> supply_curve.vertical_shift(2.0)
        """
        self.intercept += delta
        if self.slope != 0:
            self.q_intercept = -self.intercept / self.slope

    def horizontal_shift(self, delta):
        """
        Shift the curve horizontally by the given amount.

        This method shifts the supply or demand curve horizontally by the specified amount `delta`.
        Positive values of `delta` shift the curve to the right.

        Parameters
        --------
            delta (float): The amount to shift the curve horizontally.

        Returns
        --------
            None

        Example
        --------
            >>> demand_curve = Affine(10.0, -2.0)
            >>> demand_curve.horizontal_shift(1.0)
        """
        equiv_vert = delta * -self.slope
        self.intercept += equiv_vert
        if self.slope != 0:
            self.q_intercept = -self.intercept / self.slope

    def price_elasticity(self, p):
        """
        Calculate the point price elasticity at a given price.

        This method calculates the point price elasticity at the specified price `p`.

        Parameters
        --------
            p (float): The price at which to calculate the elasticity.

        Returns
        --------
            float: The point price elasticity.

        Example
        --------
            >>> demand_curve = Affine(10.0, -2.0)
            >>> demand_curve.price_elasticity(4.0)
        """

        if p < 0:
            raise ValueError('Negative price.')
        if p > self.intercept:
            raise ValueError("Price above choke price.")

        q = self.q(p)
        e = (1/self.slope) * (p/q)
        return e

    def midpoint_elasticity(self, p1, p2):
        """
        Find price elasticity between two prices using the midpoint formula.

        This method calculates the price elasticity between two prices, `p1` and `p2`,
        using the midpoint formula.

        Parameters
        --------
            p1 (float): The first price.
            p2 (float): The second price.

        Returns
        --------
            float: The price elasticity between the two prices.

        Example
        --------
            >>> demand_curve = Affine(10.0, -2.0)
            >>> demand_curve.midpoint_elasticity(3.0, 5.0)
        """

        if (p1 < 0) or (p2 < 0):
            raise ValueError('Negative price.')
        if (p1 > self.intercept) or (p2 > self.intercept):
            raise ValueError("Price above choke price.")

        mean_p = 0.5*p1 + 0.5*p2
        return self.price_elasticity(mean_p)


    def plot(self, ax = None, textbook_style = True, max_q = 10,
             color = 'black', linewidth = 2, label = True,
             xs = None, ys = None):
        """
        Plot the supply or demand curve.

        This method plots the supply or demand curve on the specified matplotlib axis.

        Parameters
        --------
            ax (matplotlib.axes._axes.Axes, optional): The matplotlib axis to use for plotting.
                If not provided, the current axes will be used.
            textbook_style (bool, optional): If True, use textbook-style plot formatting.
                Defaults to True.
            max_q (float, optional): The maximum quantity value for the plot. Defaults to 10.
            color (str, optional): The color of the plot. Defaults to 'black'.
            linewidth (int, optional): The linewidth of the plot. Defaults to 2.
            label (bool, optional): If True, label the curve and axes. Defaults to True.

        Returns
        --------
            None

        Example
        --------
            >>> demand_curve = Affine(10.0, -2.0)
            >>> demand_curve.plot()
        """
        if ax == None:
            ax = plt.gca()

        if (xs is None) and (ys is None):
            # core plot
            q_ = self.q_intercept
            if np.isnan(q_): # if slope is 0
                q_ = 10 ** 10
            if type(self).__name__ == "Supply":
                x2 = np.max([max_q, q_*2])
            else:
                x2 = q_

            y2 = self(x2)

            xs = np.linspace(0, x2, 2)
            ys = np.linspace(self.intercept, y2, 2)
        elif (xs is not None):
            if len(xs) != 2:
                raise ValueError("xs argument must be of length 2.")
            ys = [self(xs[0]), self(xs[1])]
        elif (ys is not None):
            if len(ys) != 2:
                raise ValueError("ys argument must be of length 2.")
            xs = [self.q(ys[0]), self.q(ys[1])]
        #ys = np.maximum(self.p(xs), 0)
        ax.plot(xs, ys, color = color, linewidth = linewidth)

        if textbook_style:
            textbook_axes(ax)

        if label == True:

            # Label Curves
            if type(self).__name__ == 'Demand':
                x0 = self.q_intercept * .95
            else:
                x0 = ax.get_xlim()[1] * .9

            y_delta = (ax.get_ylim()[1] - ax.get_ylim()[0])/30
            y0 = self.p(x0) + y_delta
            ax.text(x0, y0, type(self).__name__[0], va = 'bottom', ha = 'center', size = 14)

            # Label Axes
            ax.set_ylabel("Price")
            ax.set_xlabel("Quantity")

        # fix lims
        ylims = ax.get_ylim()
        ax.set_ylim(0, ylims[1])


def intersection(element1, element2):
    """
    Compute the intersection point of two lines given by `element1` and `element2`.

    Parameters
    ----------
    element1 : AffineElement
        An AffineElement representing the first line.
    element2 : AffineElement
        An AffineElement representing the second line.

    Returns
    -------
    numpy.ndarray
        A 1D array containing the y and x coordinates of the intersection point.

    Raises
    ------
    numpy.linalg.LinAlgError
        If the matrix `A` is singular, i.e., the two lines are parallel.

    Examples
    --------
    >>> line1 = AffineElement(intercept=12, slope=-1)
    >>> line2 = AffineElement(intercept=0, slope=2)
    >>> intersection(line1, line2)
    array([8., 4.])
    """
    A = np.array([[1, -element1.slope], [1, -element2.slope]])
    b = np.array([[element1.intercept], [element2.intercept]])
    yx = np.matmul(np.linalg.inv(A), b)
    return np.squeeze(yx)


def blind_sum(*curves):
    '''
    Computes the horizontal summation of AffineElement objects.

    Parameters
    ----------
    *curves : AffineElement
        The objects to be summed.

    Returns
    -------
    AffineElement
        The horizontal summation of the input curves represented as an AffineElement object.
        Returns None if no curves are provided.
    '''
    if len(curves) == 0:
        return None
    elastic_curves = [c for c in curves if c.slope == 0]
    inelastic_curves = [c for c in curves if c.slope == np.inf]
    regular_curves = [c for c in curves if c not in elastic_curves + inelastic_curves]
    
    if not elastic_curves and not inelastic_curves:
        qintercept = np.sum([-c.intercept/c.slope for c in curves])
        qslope = np.sum([1/c.slope for c in curves])
        return AffineElement(qintercept, qslope, inverse = False)
    else:
        raise Exception("Perfectly Elastic and Inelastic curves not supported")


def horizontal_sum(*curves):
    """
    Compute active curves at different price midpoints based on the p-intercepts of input curves.

    Parameters
    ----------
    *curves : sequence of AffineElements
        Variable-length argument list of Affine curve objects for which 
        the active curves are to be found.

    Returns
    -------
    tuple
        A tuple containing three elements:
        - active_curves (list): List of AffineElement objects representing
          the active curves at each price midpoint.
        - cutoffs (list): List of unique p-intercepts sorted in ascending order.
        - midpoints (list): List of midpoints computed based on the cutoffs.
    """
    elastic_curves = [c for c in curves if c.slope == 0]
    inelastic_curves = [c for c in curves if c.slope == np.inf]
    regular_curves = [c for c in curves if c not in elastic_curves + inelastic_curves]

    intercepts = [0] + [c.intercept for c in regular_curves + elastic_curves]
    cutoffs = sorted(list(set(intercepts)))
    # get a point in each region
    midpoints = [(a + b) / 2 for a, b in zip(cutoffs[:-1], cutoffs[1:])] + [cutoffs[-1]+1] 
    
    # get curves with positive quantity for each region
    active_curves = [blind_sum(*[c for c in curves if c.q(price)>0]) for price in midpoints]

    return active_curves, cutoffs, midpoints


class Affine:

    def __init__(self, intercept=None, slope=None, elements=None, inverse = True):
        """
        Initializes an Affine object with given slopes and intercepts or elements.
        The slopes correspond to elements, which are differentiated from pieces.

        The elements represent the individual curves which are horizontally summed.
        The pieces are the resulting functions for the piecewise expression describing the aggregate.

        Parameters
        ----------
        intercept : float, list of float, optional
            The y-intercept(s) of the elements.
        slope : float, list of float, optional
            The slope(s) of the elements.
        elements : list of AffineElement, optional
            A list of AffineElements whose horizontal sum defines the Affine object.
        inverse : bool, optional
            When inverse is True, it is assumed that equations are in the form P(Q).

        Raises
        ------
        ValueError
            If the lengths of `slope` and `intercept` do not match.
        """

        if elements is None:
            if isinstance(slope, (int, float)):
                slope = [slope]
            if isinstance(intercept, (int, float)):
                intercept = [intercept]

            if len(slope) != len(intercept):
                raise ValueError("Slope and intercept lengths do not match.")

            zipped = zip(slope, intercept)
            elements = [AffineElement(slope=m, intercept=b, inverse=inverse) for m, b in zipped]
        if intercept is None:
            intercept = [c.intercept for c in elements]
        if slope is None:
            slope = [c.slope for c in elements]

        pieces, cuts, mids = horizontal_sum(*elements)

        # for display _repr_latex_ behavior
        cond = [f"{cuts[i]} \\leq p \\leq {cuts[i+1]}" for i in range(len(cuts)-1)]
        cond += [f'p \\geq {cuts[-1]}']
        self.conditions = cond
        self.condition_ranges = [ (cuts[i], cuts[i+1]) for i in range(len(cuts)-1)]
        #self.expressions = [f"{c.q_intercept:g}{1/c.slope:+g}p" if c else '0' for c in pieces]
        self.expressions = [c.expression if c else '0' for c in pieces]
        self.inverse_expressions = [c.inverse_expression if c else '0' for c in pieces]

        intersections = list()
        if len(pieces):
            intersections = [intersection(pieces[i], pieces[i+1]) for i in range(len(pieces)-1) if (pieces[i]) and (pieces[i+1])]

        #maxm = np.max([intercept]), np.min([intercept])
        #choke = np.max([])

        # inverse conditions and expressions
        self.intersections = intersections
        self.pieces = pieces
        self.intercept = intercept
        self.slope = slope
        self.elements = elements

    def __call__(self, x):
        """
        Computes p given q=x. This is wrong currently.

        Parameters
        ----------
        x : float

        Returns
        -------
        float
        """
        return np.sum([np.max([0, c(x)]) for c in self.elements])

    def q(self, p):
        # returns q given p
        return np.sum([np.max([0,c.q(p)]) for c in self.elements])

    def equation(self, inverse=False):
        if inverse:
            latex_str = r"p = \begin{cases} "

            for expr, cond in zip(self.inverse_expressions, self.conditions):
                latex_str += f"{expr} & \\text{{if }} {cond} \\\\"
            latex_str += r"\end{cases}"
            return f"${latex_str}$"
        else:
            latex_str = r"q = \begin{cases} "

            for expr, cond in zip(self.expressions, self.conditions):
                latex_str += f"{expr} & \\text{{if }} {cond} \\\\"
            latex_str += r"\end{cases}"
            return f"${latex_str}$"         

    def _repr_latex_(self):
        return self.equation(inverse=False)

    def __add__(self, other):
        elements = self.elements + other.elements
        return Affine(elements=elements)

    def plot(self, ax=None):

        if ax is None:
            fig, ax = plt.subplots()

        # use intersections to 
        for piece, y_range in zip(self.pieces, self.condition_ranges):
            if piece:
                # find correct values 
                piece.plot(ax=ax, label=False, ys = y_range)

        # fix for demand and supply and inverse vs q(p)
        ax.set_ylim(0, np.max(self.intercept))

class Demand(Affine):

    def __init__(self, intercept, slope, inverse = True):
        if slope > 0:
            raise ValueError("Upward sloping demand curve.")
        super().__init__(intercept=intercept, slope=slope, inverse=inverse)
