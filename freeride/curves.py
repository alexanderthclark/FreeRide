import numpy as np
import matplotlib.pyplot as plt
import numbers
from freeride.plotting import textbook_axes, AREA_FILLS
from freeride.formula import _formula
from IPython.display import Latex, display
from bokeh.plotting import figure, show
from bokeh.models import HoverTool, ColumnDataSource


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
    def __init__(self, *coef, symbols=None, domain=None):
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

        if symbols is None:
            x, y = 'q', 'p'
        else:
            x, y = symbols
        self.x, self.y = x, y

        self.is_undefined = coef == ([],)  # helpful in sum functions
        if self.is_undefined == False:
            coef = np.squeeze(np.array(coef, ndmin=1))
            super().__init__(coef, domain=None)
        else:
            self.coef = []
            self._symbol = x
        self._domain = domain
    
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

    # Similar to numpy ABCPolyBase
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
            latex_str = f'{self.y}={self.inverse_expression}'
            return rf'${latex_str}$'
        elif hasattr(self, 'expression') and self.expression != 'undefined':
            latex_str = f'{self.y}={self.expression}'
            return rf"${latex_str}$"

        off, scale = self.mapparms()
        if off == 0 and scale == 1:
            term = self.x
            needs_parens = False
        elif scale == 1:
            term = f"{self._repr_latex_scalar(off)} + {self.x}"
            needs_parens = True
        elif off == 0:
            term = f"{self._repr_latex_scalar(scale)}{self.x}"
            needs_parens = True
        else:
            term = (
                f"{self._repr_latex_scalar(off)} + "
                f"{self._repr_latex_scalar(scale)}{self.x}"
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

        return rf"${self.y} = {body}$"


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
        To create an AffineElement object and use its methods:

        >>> demand_curve = Affine(10.0, -1.0)
        >>> demand_curve.q(4.0)  # Calculate the quantity at price p=4.0
        6.0
    """


    def __init__(self, intercept, slope, inverse=True, symbols=None):
        """
        Initialize an AffineElement with the given intercept and slope.

        This method creates an instance of the class with the specified intercept and slope.
        The parameters can be interpreted as inverse slope and intercept if the `inverse` parameter is True.

        Parameters
        --------
            intercept (float): The intercept of the affine function.
            slope (float): The slope of the affine function.
            inverse (bool, optional): If True, interprets the parameters as inverse slope
                and intercept. Defaults to True.

        Returns
        --------
            AffineElement: An AffineElement object representing the supply or demand curve.

        Example
        --------
            >>> supply_curve = AffineElement(10.0, 2.0)
        """

        if symbols is None:
            x, y = 'q', 'p'
        else:
            x, y = symbols
        self.symbols = symbols

        if slope == 0:
            if inverse:  # perfectly elastic
                self.intercept = intercept
                self.q_intercept = np.nan
                self.slope = 0

                self.inverse_expression = f'{self.intercept:g}'
                self.expression = 'undefined'
                self._symbol = x  # rhs is 0*q

            else:  # perfectly inelastic
                self.q_intercept = intercept
                self.slope = np.inf
                self.intercept = np.nan

                self.inverse_expression = 'undefined'
                self.expression = f'{self.q_intercept:g}'
                self._symbol = y  # rhs is 0*p
            self.coef = (self.intercept, self.slope)
            super().__init__(self.coef, symbols=symbols)
        else:
            if not inverse:
                slope, intercept = 1/slope, -intercept/slope

            coef = (intercept, slope)
            super().__init__(coef, symbols=symbols)
            self.intercept = intercept
            self.slope = slope
            self.q_intercept = -intercept/slope
            self.inverse_expression = f'{intercept:g}{slope:+g}{x}'
            self.expression = f'{self.q_intercept:g}{1/slope:+g}{y}'

    def __call__(self,x):
        if self.slope == 0:
            return self.intercept
        elif self.slope == np.inf:
            raise Exception(f"Undefined (perfectly inelastic at {self.q_intercept})")
        else:
            return self.intercept + self.slope*x

    def vertical_shift(self, delta, inplace=True):
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
        new_intercept = self.intercept + delta
        #if self.slope != 0:
        #    self.q_intercept = -self.intercept / self.slope
        if inplace:
            self.__init__(new_intercept, self.slope)
        else:
            return AffineElement(new_intercept, self.slope, symbols=self.symbols)

    def horizontal_shift(self, delta, inplace=True):
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
        if self.slope == np.inf:
            new_q_intercept = self.q_intercept + delta
            if inplace:
                self.__init__(new_q_intercept, 0, inverse=False)
            else:
                return AffineElement(new_q_intercept, 0, inverse=False, symbols=self.symbols)
        else:
            equiv_vert = delta * -self.slope
            new_intercept = self.intercept + equiv_vert
            #if self.slope != 0:
            #    self.q_intercept = -self.intercept / self.slope
            if inplace:
                self.__init__(new_intercept, self.slope)
            else:
                return AffineElement(new_intercept, self.slope, symbols=self.symbols)

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


    def plot(self, ax=None, textbook_style=True, max_q=None,
             label=True, **kwargs):
        """
        Plot the affine curve.

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
            >>> demand_curve = AffineElement(10.0, -2.0)
            >>> demand_curve.plot()
        """
        if ax == None:
            ax = plt.gca()

        # core plot
        if self._domain:
            x1, x2 = self._domain
            if x2 == np.inf:
                x2 = max_q if max_q else x1*2 + 1
        else:
            x1 = 0
            q_ = self.q_intercept
            if np.isnan(q_): # if slope is 0
                q_ = 10 ** 10
            if type(self).__name__ == "Supply":
                x2 = np.max([10, q_*2])
            else:
                x2 = q_

        y1 = self(x1)
        y2 = self(x2)

        xs = np.linspace(x1, x2, 2)
        ys = np.linspace(y1, y2, 2)
        
        if 'color' not in kwargs:
            kwargs['color'] = 'black'
        ax.plot(xs, ys, **kwargs)

        if textbook_style:
            textbook_axes(ax)

        if label == True:

            # Label Curves
            #if type(self).__name__ == 'Demand':
            #    x0 = self.q_intercept * .95
            #else:
            #if name:
            #    x0 = ax.get_xlim()[1] * .9
            #    y_delta = (ax.get_ylim()[1] - ax.get_ylim()[0])/30
            #    y0 = self.p(x0) + y_delta
            #    ax.text(x0, y0, name, va = 'bottom', ha = 'center', size = 14)

            # Label Axes
            ax.set_ylabel("Price")
            ax.set_xlabel("Quantity")

        # fix lims
        ylims = ax.get_ylim()
        ax.set_ylim(0, ylims[1])

        return ax

    def plot_area(self, p, q=None, ax=None, zorder=-1, color=None, alpha=None):
        '''
        Plot surplus region 
        '''
        if ax is None:
            ax = self.plot()

        if q is None:
            q0 = np.min(self._domain)
            q1 = np.max(self._domain)
            q = q0, q1
        else:
            q0, q1 = q

        qstar = self.q(p)

        if q0 < qstar <= q1:
            q = q0, qstar
        elif q1 < qstar:
            q = q0, q1
        elif qstar < q0:
            return ax

        p01 = self.p(q[0]), self.p(q[1])

        ax.fill_between(q, p01, p,
                        zorder=zorder,
                        color=color,
                        alpha=alpha)

        return ax

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

    # remove negative intercepts
    cutoffs = [c for c in cutoffs if c>=0]

    # get a point in each region
    midpoints = [(a + b) / 2 for a, b in zip(cutoffs[:-1], cutoffs[1:])] + [cutoffs[-1]+1] 
    
    # get curves with positive quantity for each region
    active_curves = [blind_sum(*[c for c in curves if c.q(price)>0]) for price in midpoints]

    return active_curves, cutoffs, midpoints


def ppf_sum(*curves, comparative_advantage=True):

    slope_and_curves = sorted([(s.slope, s) for s in curves], reverse=comparative_advantage)
    curves = [t[1] for t in slope_and_curves]
    x_intercepts = [c.q_intercept for c in curves]
    y_intercepts = [c.intercept for c in curves]
    y_int = sum([s.intercept for s in curves])
    x_int = sum([s.q_intercept for s in curves])

    for key, ppf in enumerate(curves):

        previous_x = sum(x_intercepts[0:key])
        below_y = sum(y_intercepts[key+1:])

        new = ppf.vertical_shift(below_y, inplace=False)
        new.horizontal_shift(previous_x)
        curves[key] = new

        new._domain = previous_x + ppf.q_intercept, previous_x

    return curves


class BaseAffine:

    def __init__(self, intercept=None, slope=None, elements=None, inverse=True):
        """
        Initialize the BaseAffine object.

        Parameters
        ----------
        intercept : float or list of floats, optional
            The intercept(s) of the affine transformation. Default is None.
        slope : float or list of floats, optional
            The slope(s) of the affine transformation. Default is None.
        elements : list of AffineElement, optional
            List of AffineElement objects. If provided, it will override `intercept` and `slope`. Default is None.
        inverse : bool, optional
            Indicates if the transformation should be inverted. Default is True.

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
        self.elements = elements

        if intercept is None:
            intercept = [c.intercept for c in elements]
        if slope is None:
            slope = [c.slope for c in elements]

        self.intercept = intercept
        self.slope = slope

    @classmethod
    def from_two_points(cls, x1, y1, x2, y2):
        """
        Creates an Affine object from two points.
        """
        A = np.array([[x1, 1], [x2, 1]])
        b = np.array([y1, y2])
        slope, intercept = np.linalg.solve(A, b)

        return cls(slope=slope, intercept=intercept)
    
    @classmethod
    def from_points(cls, xy_points):
        """
        Creates an Affine object from two points.

        In the future, this might be extended to allow for three or more points.
        """

        A_array = [[qp[0], 1] for qp in xy_points]
        p_vals = [qp[1] for qp in xy_points]

        A = np.array(A_array)
        b = np.array(p_vals)
        slope, intercept = np.linalg.solve(A, b)

        return cls(slope=slope, intercept=intercept)

    @classmethod
    def from_formula(cls, equation: str):
        intercept, slope = _formula(equation)
        return cls(slope=slope, intercept=intercept)

    def horizontal_shift(self, delta, inplace=True):
        new_elements = [e.horizontal_shift(delta, inplace=False) for e in self.elements]
        if inplace:
            self.__init__(elements=new_elements)
        else:
            return Affine(elements=new_elements)

    def vertical_shift(self, delta, inplace=True):
        new_elements = [e.vertical_shift(delta, inplace=False) for e in self.elements]
        if inplace:
            self.__init__(elements=new_elements)
        else:
            return Affine(elements=new_elements)


class Affine(BaseAffine):
    """
    A class to represent a piecewise affine function.
    """

    def __init__(self, intercept=None, slope=None, elements=None, inverse=True):
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

        super().__init__(intercept, slope, elements, inverse)

        pieces, cuts, mids = horizontal_sum(*self.elements)
        self.pieces = pieces

        # store piecewise info
        sections = [(cuts[i], cuts[i+1]) for i in range(len(cuts)-1)]
        qsections = [ (self.q(ps[0]), self.q(ps[1]))  for ps in sections]
        sections.append( (cuts[-1], np.inf) )
        if self.q(cuts[-1]+1) <= 0: # demand
            qsections.append((0,0))
        elif len(qsections): # supply
            maxq = np.max(qsections[-1])
            qsections.append((maxq, np.inf))
        else: # supply
            qsections.append((0, np.inf))
        self.psections = sections
        self.qsections = qsections
        self._set_piece_domains()

        # for display _repr_latex_ behavior
        cond = [f"{cuts[i]} \\leq p \\leq {cuts[i+1]}" for i in range(len(cuts)-1)]
        cond += [f'p \\geq {cuts[-1]}']
        self.conditions = cond
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
        #self.intercept = intercept
        #self.slope = slope

    def _set_piece_domains(self):
        for piece, qs in zip(self.pieces, self.qsections):
            if piece:
                piece._domain = qs
                piece._domain_length = np.max(qs) - np.min(qs)

    def _get_active_piece(self, q):

        for piece in [piece for piece in self.pieces if piece]:
            q0, q1 = np.min(piece._domain), np.max(piece._domain)

            # this has to be closed on the right and open on the left
            # there has to be area to the left when calc surplus
            if q0 < q <= q1:
                return piece
        return None

    def __call__(self, x):
        """
        Computes p given q=x.

        Parameters
        ----------
        x : float

        Returns
        -------
        float
        """

        for piece in self.pieces:
            if piece:
                a, b = piece._domain
                if (a <= x <= b) or (a >= x >= b):
                    return piece(x)
        # might be x out of limits
        return np.nan
        #return np.sum([np.max([0, c(x)]) for c in self.elements])

    def q(self, p):
        # returns q given p
        return np.sum([np.max([0,c.q(p)]) for c in self.elements])
    
    def p(self, q):
        # returns p given q
        return self.__call__(q)

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

    def price_elasticity(self, p, delta=.000001):
        q = self.q(p)
        pt = np.array([p,q])
        if self.intersections and np.any(pt == self.intersections, axis=1).max():
            below = self.price_elasticity(p - delta)
            above = self.price_elasticity(p + delta)
            s = f"\nElasticity is {below:+.3f} below P={p} and {above:+.3f} above."
            raise ValueError("Point elasticity is not defined at a kink point."+s)
        else:
            # Get q-domains
            pc = [p for p in self.pieces if p and (q > np.min(p._domain)) and (q < np.max(p._domain))] 
            assert len(pc) == 1
            return pc[0].price_elasticity(p)

    def _repr_latex_(self):
        return self.equation(inverse=False)

    @property
    def inverse_equation(self):
        display(Latex(self.equation(inverse=True)))

    def __add__(self, other):
        elements = self.elements + other.elements
        return type(self)(elements=elements)

    def plot(self, ax=None, set_lims=True, max_q=None, label=True, **kwargs):
        '''
        Plot the Affine object.

        Parameters
        ----------
        ax : matplotlib.axes.Axes, optional
            The axes on which to plot. If None, a new figure and axes will be created.
        set_lims : bool, optional
            Whether to automatically set the limits for the axes. Default is True.
        max_q : float, optional
            The maximum quantity to consider for setting the x-axis limit. If None, it will be automatically determined.
        **kwargs : dict
            Additional keyword arguments to customize the plot. These can include any valid `matplotlib.pyplot` function keyword, such as:
            
            title : str
                The title of the plot.
            xlabel : str
                The label for the x-axis.
            ylabel : str
                The label for the y-axis.
            xlim : tuple
                The limits for the x-axis, e.g., (xmin, xmax).
            ylim : tuple
                The limits for the y-axis, e.g., (ymin, ymax).

        Returns
        -------
        None
        '''
        if ax is None:
            fig, ax = plt.subplots()

        param_names = ['color', 'linewidth', 'linestyle', 'lw', 'ls']
        plot_dict = {key: kwargs[key] for key in kwargs if key in param_names}
        # Plot each element
        for piece in self.pieces:
            if piece:
                piece.plot(ax=ax, label=label, max_q=max_q, **plot_dict)

        # check limits
        if set_lims:
            ylim = ax.get_ylim()
            xlim = ax.get_xlim()
            if ylim[1] <= np.max(self.intercept):
                ax.set_ylim(0, np.max(self.intercept)*1.01)

            flat_q = sorted([i for tup in self.qsections for i in tup])
            flat_p = sorted([i for tup in self.psections for i in tup])
            if max_q is None:
                if np.inf in flat_q:
                    max_q = 1.5*flat_q[-2]
                else:
                    max_q = flat_q[-1]
            if np.inf in flat_p:
                max_p = np.max([self(max_q), 1.5*flat_p[-2]])
            else:
                max_p = np.max([self(max_q), 1.5*flat_p[-1]])

            # don't decrease limits relative to starting point
            ax.set_ylim(0, np.max([max_p, ylim[1]]))
            ax.set_xlim(0, np.max([max_q, 1, xlim[1]]))
            # fix for demand and supply and inverse vs q(p)
            #ax.set_xlim(0, np.max(self.intercept))

        # Run additional parameters as pyplot functions
        # xlim or ylim will overwrite the previous set_lims behavior
        for key, value in kwargs.items():
            if hasattr(plt, key):
                plt_function = getattr(plt, key)
                if callable(plt_function):
                    # Unpack sequences (e.g. for plt.text)
                    if isinstance(value, tuple) or isinstance(value, list):
                        plt_function(*value)
                    else:
                        plt_function(value)

        # Label intercepts and intersections
        if label:
            xticks, yticks = [self.q(0)], [self.p(0)]
            for point in self.intersections:
                x, y = point[1], point[0]
                xticks.append(x)
                yticks.append(y) # P is first element

                sty = {"lw":0.5, "ls": 'dotted', "color": 'gray'}
                ax.plot([x,x], [0,y], **sty)
                ax.plot([0,x], [y,y], **sty)

            ax.set_xticks(xticks)
            ax.set_yticks(yticks)

        return ax

    def plot_surplus(self, p, ax=None, color=None, max_q=None, alpha=None):

        if (color is None) and isinstance(self, Supply):
            color = AREA_FILLS[1]
        elif color is None:
            color = AREA_FILLS[0]

        if ax is None:
            ax = self.plot(max_q=max_q)
        qstar = self.q(p)
        for piece in self.pieces:
            if piece:
                piece.plot_area(p,
                             ax=ax,
                             color=color,
                             alpha=alpha)
        return ax
                
    def surplus(self, p):
        '''
        Returns surplus area. The areas are negative for producer surplus.
        '''
        q = self.q(p)

        if q > 0:

            # find inframarginal surplus
            trapezoids = [piece for piece in self.pieces if piece and (np.max(piece._domain) < q)]
            trap_areas = [piece._domain_length*(np.mean([piece.p(piece._domain[0]),piece.p(piece._domain[1])])-p) for piece in trapezoids]

            # find the last unit demanded and get surplus from that curve
            last_piece = self._get_active_piece(q)
            height = last_piece.p(np.min(last_piece._domain)) - p
            base = q - np.min(last_piece._domain)
            tri_area = 0.5 * height * base

            return tri_area + np.sum(trap_areas)

        else:
            return 0

class Demand(Affine):

    def __init__(self, intercept=None, slope=None, elements=None, inverse = True):
        """
        Initializes a Demand curve object.
        """
        super().__init__(intercept, slope, elements, inverse)
        self._check_slope()

    def _check_slope(self):
        for slope in self.slope:
            if slope > 0:
                raise Exception("Upward-sloping demand curve.")
        if self.q(0) < 0:
            raise Exception("Negative demand.")

    def consumer_surplus(self, p):
        return self.surplus(p)

class Supply(Affine):

    def __init__(self, intercept=None, slope=None, elements=None, inverse=True):
        """
        Initializes a Supply curve object.
        """
        super().__init__(intercept, slope, elements, inverse)
        self._check_slope()

    def _check_slope(self):
        for slope in self.slope:
            if slope < 0:
                raise Exception("Downard-sloping supply curve.")

    def producer_surplus(self, p):
        return -self.surplus(p)


class Constraint(BaseAffine):

    def __init__(self, p1, p2, endowment=1, name1=None, name2=None, elements=None, inverse=True):
        '''
        Incomplete.
        '''

        if elements is None:
            slope = -p1/p2
            intercept = endowment/p2
            super().__init__(intercept, slope, elements, inverse)
        else:
            super().__init__(None, None, elements, inverse)


class PPF(BaseAffine):
    '''
    Production possibilities frontier.
    '''

    def __init__(self, intercept=None, slope=None, elements=None, inverse=True):
        '''
        Initializes a PPF object with given slope and intercept or elements.

        Parameters
        ----------
        intercept : float or list of float, optional
            The y-intercept(s) of the elements.
        slope : float or list of float, optional
            The slope(s) of the elements.
        elements : list of AffineElement, optional
            A list of AffineElements whose horizontal sum defines the PPF.
        inverse : bool, optional
            When inverse is True, it is assumed that equations are in the form P(Q).

        Raises
        ------
        ValueError
            If the lengths of `slope` and `intercept` do not match.
        '''
        super().__init__(intercept, slope, elements, inverse)
        self.pieces = ppf_sum(*self.elements)


    def __add__(self, other):
        elements = self.elements + other.elements
        return type(self)(elements=elements)

    def plot(self, ax=None, set_lims=True, max_q=None, label=True, backend='mpl', **kwargs):
        '''
        Plot the ppf.
        '''

        if backend == 'bokeh':
            p = figure(width=400, height=400, tools="")
            lines_data = {'xs': [], 'ys': [], 'label': []}

            for key, piece in enumerate(self.pieces):
                x0, x1 = piece._domain
                xx = np.linspace(x0, x1)
                yy = [piece(u) for u in xx]
                lines_data['xs'].append(xx)
                lines_data['ys'].append(yy)
                lines_data['label'].append(f'Piece {key}')
            source = ColumnDataSource(data=lines_data)

            p.multi_line(xs='xs', ys='ys', source=source, line_width=2)
            # Add HoverTool
            hover = HoverTool(
                tooltips=[('', "@label")],
                renderers=[p.renderers[-1]])
            p.add_tools(hover)

            return p

        elif backend == 'mpl':
            if ax is None:
                fig, ax = plt.subplots()

            param_names = ['color', 'linewidth', 'linestyle', 'lw', 'ls', 'marker', 'markersize']
            plot_dict = {key: kwargs[key] for key in kwargs if key in param_names}
            # Plot each element
            for piece in self.pieces:
                if piece:
                    piece.plot(ax=ax, label=label, max_q=max_q, **plot_dict)

            if label:
                ax.set_xlabel("Good 1")
                ax.set_ylabel("Good 2")

            # Run additional parameters as pyplot functions
            # xlim or ylim will overwrite the previous set_lims behavior
            for key, value in kwargs.items():
                if hasattr(plt, key):
                    plt_function = getattr(plt, key)
                    if callable(plt_function):
                        # Unpack sequences (e.g. for plt.text)
                        if isinstance(value, tuple) or isinstance(value, list):
                            plt_function(*value)
                        else:
                            plt_function(value)

            return ax