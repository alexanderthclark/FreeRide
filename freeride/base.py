import numpy as np
import matplotlib.pyplot as plt
import numbers
from freeride.plotting import textbook_axes, AREA_FILLS
from freeride.formula import _formula, _quadratic_formula
from IPython.display import Latex, display


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
        self.set_symbols(symbols)
        self.is_undefined = coef == ([],)  # helpful in sum functions
        if self.is_undefined == False:
            coef = np.squeeze(np.array(coef, ndmin=1))
            super().__init__(coef, domain=None, symbol=self._symbol)
        else:
            self.coef = []
            self._symbol = self.x
        # user-defined domain for building piecewise functions
        self._domain = domain

    def in_domain(self, x):
        if self._domain:
            d = sorted(self._domain)
            return (d[0] <= x <= d[1])
        else:
            return True

    def __call__(self, x):
        if self.is_undefined:
            raise ValueError("Polynomial is undefined.")
        elif self.in_domain(x):
            return super().__call__(x)
        else:
            raise ValueError(f"{self.x}={x} is outside of the function domain, {self._domain}.")

    def __bool__(self):
        return not self.is_undefined

    def set_symbols(self, symbols):
        self.symbols = symbols
        if isinstance(symbols, str):
            x = symbols
            y = None
        elif symbols is None:
            x, y = 'q', 'p'
        elif len(symbols)==2:
            x, y = symbols
        else:
            raise Exception("symbols not properly set")
        self.x, self.y = x, y
        self.symbols = self.x, self.y
        self._symbol = self.x

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

    def plot(self, ax=None, label=None, max_q=100, min_plotted_q=0, textbook_style=True):
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

        if textbook_style:
            textbook_axes(ax)

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
        if self.y:
            return rf"${self.y} = {body}$"
        else:
            return rf"${self.x} \mapsto {body}$"

    def vertical_shift(self, delta, inplace=True):
        """
        Shift the curve vertically by the given amount.
        """
        if inplace:
            self.coef[0] += delta
        else:
            new_coef = self.coef
            new_coef[0] += delta
            return self.__class__(*new_coef, symbols=self.symbols)


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
        elif isinstance(symbols, str):
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

    def __call__(self, x):
        if self.slope == np.inf:
            raise Exception(f"Undefined (perfectly inelastic at {self.q_intercept})")
        else:
            return self.intercept + self.slope*x

    def __mul__(self, scalar):
        return type(self)(intercept=self.intercept, slope=self.slope*(1/scalar), inverse=True, symbols=self.symbols)
    
    def __rmul__(self, scalar):
        return self.__mul__(scalar)

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
            return self.__class__(new_intercept, self.slope, symbols=self.symbols)

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
                return self.__class__(new_q_intercept, 0, inverse=False, symbols=self.symbols)
        else:
            equiv_vert = delta * -self.slope
            new_intercept = self.intercept + equiv_vert
            #if self.slope != 0:
            #    self.q_intercept = -self.intercept / self.slope
            if inplace:
                self.__init__(new_intercept, self.slope)
            else:
                return self.__class__(new_intercept, self.slope, symbols=self.symbols)

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

    def plot_area(self, p, q=None, ax=None, zorder=-1, color=None, alpha=None, force=False):
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

        if not force:
            qstar = self.q(p)

            if q0 < qstar <= q1:
                q = q0, qstar
            elif q1 < qstar:
                q = q0, q1
            elif qstar < q0: # plot nothing if no surplus in region
                return ax

        p01 = self.p(q[0]), self.p(q[1])

        ax.fill_between(q, p01, p,
                        zorder=zorder,
                        color=color,
                        alpha=alpha)

        return ax


class QuadraticElement(PolyBase):
    """
    Extends the PolyBase class and represents a quadratic function used in revenue and cost curves.
    """

    def __init__(self, intercept, linear_coef, quadratic_coef, symbols=None, domain=None):
        """
        Initialize QuadraticElement class.
        """

        if symbols is None:
            symbols = 'q'
        self.intercept = intercept
        self.linear_coef = linear_coef
        self.quadratic_coef = quadratic_coef
        self.coef = (intercept, linear_coef, quadratic_coef)
        super().__init__(self.coef, symbols=symbols)
        self._domain = domain

    def horizontal_shift(self, delta, inplace=True):
        """
        Shift the curve horizontally by the given amount.

        This method shifts the supply or demand curve horizontally by the specified amount `delta`.
        Positive values of `delta` shift the curve to the right.

        """
        # a + b(x-delta) + c(x-delta)^2
        a, b, c = self.coef
        new_intercept = a - b*delta + c*delta**2
        new_linear_coef = b - 2*c*delta
        new_quadratic_coef = c
        coef = new_intercept, new_linear_coef, new_quadratic_coef
        if inplace:
            self.__init__(*coef, symbols=self.symbols)
        else:
            return self.__class__(*coef, symbols=self.symbols)

    def plot(self, ax=None, textbook_style=True, max_q=100,
             label=True, **kwargs):
        """
        """
        if ax is None:
            ax = plt.gca()

        # core plot
        if self._domain:
            x1, x2 = self._domain
        else:
            x1, x2 = 0, max_q

        xs = np.linspace(x1, x2, 1000)
        ys = self(xs)

        if 'color' not in kwargs:
            kwargs['color'] = 'black'
        ax.plot(xs, ys, **kwargs)

        if textbook_style:
            textbook_axes(ax)

        if label == True:
            #ax.set_ylabel("Price")
            ax.set_xlabel("Quantity")

        return ax

    def plot_area_below(self, q0, q1, ax=None, zorder=-1, color=None, alpha=None):
        '''
        Plot surplus region
        '''
        if ax is None:
            ax = self.plot()

        xs = np.linspace(q0, q1, 100)
        ys = self(xs)
        ax.fill_between(xs, 0, ys,
                        zorder=zorder,
                        color=color,
                        alpha=alpha)

        return ax

    def plot_area_above(self, q0, q1, y, ax=None, zorder=-1, color=None, alpha=None):
        '''
        Plot surplus region
        '''
        if ax is None:
            ax = self.plot()

        xs = np.linspace(q0, q1, 100)
        ys = self(xs)
        ax.fill_between(xs, ys, y,
                        zorder=zorder,
                        color=color,
                        alpha=alpha)
        return ax

    @classmethod
    def from_formula(cls, equation: str):
        a, b, c = _quadratic_formula(equation)
        return cls(c, b, a, domain = (-np.inf, np.inf))
