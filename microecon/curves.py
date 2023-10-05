import numpy as np
import matplotlib.pyplot as plt
import numbers
from microecon.plotting import textbook_axes
from microecon.utilities import args_to_array


class PolyBase(np.polynomial.Polynomial):
    """
    A base class for polynomial functions with added methods.
    The independent variable is q instead of x to align with typical price-quantity axes.
    The dependent variable is is explicitly named as p instead of y.

    This class extends NumPy's polynomial class and provides additional methods for
    working with polynomial functions.

    .. math::

       p = \sum_{k=0}^n c_k q^k

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
    def __init__(self, *coef):
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
        coef = args_to_array(coef)
        super().__init__(coef, symbol='q')

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


class Affine(PolyBase):
    """
    A class representing an affine function for supply or demand.

    This class extends the PolyBase class and represents an affine function commonly
    used in supply and demand curves.

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
        if not inverse:
            slope, intercept = 1/slope, -intercept/slope

        coef = (intercept, slope)
        super().__init__(coef)
        self.intercept = intercept
        self.slope = slope

        if slope != 0:
            self.q_intercept = -intercept/slope
        else:
            self.q_intercept = np.nan

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
             color = 'black', linewidth = 2, label = True):
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

        # core plot
        q_ = self.q_intercept
        if np.isnan(q_): # if slope is 0
            q_ = 10 ** 10
        if type(self).__name__ == "Supply":
            x2 = np.max([max_q, q_*2])
        else:
            x2 = q_

        y2 = self(x2)

        xs = np.linspace(0, x2,2)
        ys = np.linspace(self.intercept, y2, 2)
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

class PiecewiseAffine:
    """
    Represents the horizontal summation of multiple Affine objects.

    This class combines multiple Affine objects to represent a piecewise linear function
    that results from horizontally summing multiple supply or demand curves.

    Parameters
    --------
        curve_array (list of Affine, optional): An array of Affine objects to be combined.
            Defaults to None.
        *args: Additional Affine objects passed as arguments to be included in the summation.

    Attributes
    --------
        curve_array (list of Affine): An array of Affine objects used in the summation.
        is_demand (bool): True if the resulting curve represents demand, False if supply.

    Methods
    --------
        q(self, p):
            Find the aggregate quantity at the given price by summing the individual Affine curves.

    Example
    --------
        >>> curve1 = Affine(10.0, -2.0)
        >>> curve2 = Affine(5.0, -1.0)
        >>> piecewise_curve = PiecewiseAffine(curve1, curve2)
    """
    def __init__(self, curve_array = None, *args):
        """
        Initialize a PiecewiseAffine object with a list of Affine objects.

        Parameters
        --------
            curve_array (list of Affine, optional): An array of Affine objects to be combined.
                Defaults to None.
            *args: Additional Affine objects passed as arguments to be included in the summation.

        Returns
        --------
            PiecewiseAffine: A PiecewiseAffine object representing the combined curve.

        Example
        --------
            >>> curve1 = Affine(10.0, -2.0)
            >>> curve2 = Affine(5.0, -1.0)
            >>> piecewise_curve = PiecewiseAffine(curve1, curve2)
        """

        if (curve_array == None):
            curve_array = list(args)
        self.curve_array = curve_array
        slopes = sorted([x.slope for x in self.curve_array])
        self.is_demand = slopes[0] < 0
        self.is_supply = not self.is_demand

    def q(self, p):
        """
        Find the aggregate quantity at the given price by summing the individual Affine curves.

        This method calculates the aggregate quantity corresponding to the given price `p`
        by summing the individual Affine curves that make up the piecewise curve.

        Parameters
        --------
            p (float): The price at which to calculate the aggregate quantity.

        Returns
        --------
            float: The aggregate quantity at the specified price.

        Example
        --------
            >>> curve1 = Affine(10.0, -2.0)
            >>> curve2 = Affine(5.0, -1.0)
            >>> piecewise_curve = PiecewiseAffine(curve1, curve2)
            >>> piecewise_curve.q(4.0)
        """
        total_q = 0
        for curve in self.curve_array:
            total_q += np.max([0,curve.q(p)])
        return total_q

class PerfectlyElastic:
    pass
class PerfectlyInelastic:
    pass

class Demand(Affine):
    """
    Represents a demand curve, extending the Affine class.

    This class represents a demand curve, which extends the Affine class to include specific
    methods and properties related to demand curves.

    Parameters
    ----------
        intercept (float): The intercept of the demand curve.
        slope (float): The slope of the demand curve.
        inverse (bool, optional): If True, interprets the parameters as inverse slope
            and intercept. Defaults to True.

    Attributes
    ----------
        intercept (float): The intercept of the demand curve.
        slope (float): The slope of the demand curve.

    Methods
    ----------
        __init__(self, intercept, slope, inverse=True):
            Initialize a Demand object with intercept and slope.
        consumer_surplus(self, p):
            Calculate consumer surplus at a given price.
        plot_surplus(self, p, ax=None):
            Plot consumer surplus for a given price.

    Example
    ----------
        >>> demand_curve = Demand(10.0, -2.0)
        >>> demand_curve.plot()
    """

    def __init__(self, intercept, slope, inverse = True):
        """
        Initialize a Demand object with the given intercept and slope.

        This method creates an instance of the Demand class with the specified intercept and slope.
        The parameters can be interpreted as inverse slope and intercept if the `inverse` parameter is True.

        Parameters
        ----------
            intercept (float): The intercept of the demand curve.
            slope (float): The slope of the demand curve.
            inverse (bool, optional): If True, interprets the parameters as inverse slope
                and intercept. Defaults to True.

        Returns
        ----------
            Demand: A Demand object representing the demand curve.

        Example
        ----------
            >>> demand_curve = Demand(10.0, -2.0)
        """
        super().__init__(intercept, slope, inverse)

        if self.slope > 0:
            raise ValueError("Upward sloping demand curve.")

    def consumer_surplus(self, p):
        """
        Calculate consumer surplus at a given price.

        This method calculates the consumer surplus at the specified price `p`.

        Parameters
        ----------
            p (float): The price at which to calculate consumer surplus.

        Returns
        ----------
            float: The consumer surplus at the specified price.

        Example
        ----------
            >>> demand_curve = Demand(10.0, -2.0)
            >>> demand_curve.consumer_surplus(4.0)
        """
        q = np.max([0, self.q(p)])
        return (self.p(0) - p) * q * 0.5


    def plot_surplus(self, p, ax = None):
        """
        Plot consumer surplus.

        This method plots the consumer surplus for a given price `p` on the specified matplotlib axis.

        Parameters
        ----------
            p (float): The price at which to plot consumer surplus.
            ax (matplotlib.axes._axes.Axes, optional): The matplotlib axis to use for plotting.
                If not provided, the current axes will be used.

        Returns
        ----------
            None

        Example
        ----------
            >>> demand_curve = Demand(10.0, -2.0)
            >>> demand_curve.plot_surplus(4.0)
        """

        if ax == None:
            ax = plt.gca()

        if p <= self.intercept:
            cs_plot = ax.fill_between([0, self.q(p)], y1 = [self.intercept, p], y2 = p,  alpha = 0.1)

class Supply(Affine):
    """
    Represents a supply curve, extending the Affine class.

    This class represents a supply curve, which extends the Affine class to include specific
    methods and properties related to supply curves.

    Parameters
    ----------
        intercept (float): The intercept of the supply curve.
        slope (float): The slope of the supply curve.
        inverse (bool, optional): If True, interprets the parameters as inverse slope
            and intercept. Defaults to True.

    Attributes
    ----------
        intercept (float): The intercept of the supply curve.
        slope (float): The slope of the supply curve.

    Methods
    ----------
        __init__(self, intercept, slope, inverse=True):
            Initialize a Supply object with intercept and slope.
        producer_surplus(self, p):
            Calculate producer surplus at a price, disallowing negative costs/WTS.
        plot_surplus(self, p, ax=None):
            Plot producer surplus for a given price.

    Example
    ----------
        >>> supply_curve = Supply(10.0, 2.0)
        >>> supply_curve.plot()
    """
    def __init__(self, intercept, slope, inverse = True):
        """
        Initialize a Supply object with the given intercept and slope.

        This method creates an instance of the Supply class with the specified intercept and slope.
        The parameters can be interpreted as inverse slope and intercept if the `inverse` parameter is True.

        Parameters
        ----------
            intercept (float): The intercept of the supply curve.
            slope (float): The slope of the supply curve.
            inverse (bool, optional): If True, interprets the parameters as inverse slope
                and intercept. Defaults to True.

        Returns
        ----------
            Supply: A Supply object representing the supply curve.

        Example
        ----------
            >>> supply_curve = Supply(10.0, 2.0)
        """
        super().__init__(intercept, slope, inverse)

        if self.slope < 0:
            raise ValueError("Downward sloping supply curve.")


    def producer_surplus(self, p):
        """
        Calculate producer surplus at a price, disallowing negative costs/WTS.

        This method calculates the producer surplus at the specified price `p`,
        disallowing negative costs/WTS (willingness to supply).

        Parameters
        ----------
            p (float): The price at which to calculate producer surplus.

        Returns
        ----------
            float: The producer surplus at the specified price.

        Example
        ----------
            >>> supply_curve = Supply(10.0, 2.0)
            >>> supply_curve.producer_surplus(6.0)
        """
        if p <= self.p(0):
            return 0

        q = self.q(p)


        if self.q_intercept > 0:
            rectangle_width = np.min([q,self.q_intercept])
            rectangle_area = rectangle_width * p
            triangle_area = np.max([q - self.q_intercept]) * p * 0.5
            return rectangle_area + triangle_area

        return (p - self.p(0)) * q * 0.5


    def plot_surplus(self, p, ax = None):
        """
        Calculate producer surplus at a price, disallowing negative costs/WTS.

        This method calculates the producer surplus at the specified price `p`,
        disallowing negative costs/WTS (willingness to supply).

        Parameters
        ----------
            p (float): The price at which to calculate producer surplus.

        Returns
        ----------
            float: The producer surplus at the specified price.

        Example
        ----------
            >>> supply_curve = Supply(10.0, 2.0)
            >>> supply_curve.producer_surplus(6.0)
        """
        if p < 0:
            raise ValueError("Negative price.")

        if ax == None:
            ax = plt.gca()
        q = self.q(p)
        # fix later for negative

        if q <= 0:
            return None

        qq = np.min([q, self.q_intercept])

        if q > self.q_intercept > 0:

            rectangle_plot = ax.fill_between([0, qq, q], y1 = [0,0,p], y2 = p, color = 'C1', alpha = 0.1)

        elif self.q_intercept >= q > 0:
            rectangle_plot = ax.fill_between([0,q], y1 = 0, y2 = p, color = 'C1', alpha = 0.1)

        else:
            ps_plot = ax.fill_between([0,q], y1 = [self.intercept, p], y2 = p, color = 'C1', alpha = 0.1)


############################################################
#### Cost Classes

class Cost(PolyBase):
    """
    Polynomial cost curve.

    This class represents a polynomial cost curve and extends the PolyBase class. It provides methods
    for calculating costs, finding the efficient scale, breakeven price, shutdown price, and plotting
    various cost-related curves.

    Parameters
    ----------
        *coef (float or array-like): Coefficients of the polynomial cost curve.

    Attributes
    ----------
        coef (array-like): Coefficients of the polynomial cost curve.

    Methods
    ----------
        __init__(self, *coef):
            Initialize a Cost object with coefficients.
        _repr_latex_(self):
            Generate a LaTeX representation of the cost curve.
        cost(self, q):
            Calculate the cost at a given quantity.
        variable_cost(self):
            Return a Cost object representing the variable cost.
        marginal_cost(self):
            Return a Cost object representing the marginal cost.
        average_cost(self):
            Return an AverageCost object representing the average cost.
        efficient_scale(self):
            Find the quantity that minimizes average cost.
        breakeven_price(self):
            Find the price such that economic profit is zero (perfect competition).
        shutdown_price(self):
            Find the price such that total revenue equals total variable cost (perfect competition).
        long_run_plot(self, ax=None):
            Plot the long-run average cost and marginal cost curves.
        cost_profit_plot(self, p, ax=None, items=['tc', 'tr', 'profit']):
            Plot cost, revenue, and profit curves at a given price.

    Example
    ----------
        >>> cost_curve = Cost(0.5, 0.1, -0.02)
        >>> cost_curve.cost(10)
    """

    def __init__(self, *coef):
        """
        Initialize a Cost object with the specified coefficients.

        This method creates an instance of the Cost class with the given coefficients.

        Parameters
        ----------
            *coef (float or array-like): Coefficients of the polynomial cost curve.

        Returns
        ----------
            Cost: A Cost object representing the polynomial cost curve.

        Example
        ----------
            >>> cost_curve = Cost(0.5, 0.1, -0.02)
        """

        # if there's an array just use the array
        if type(coef[0]) not in [float, int]:

            if len(coef) > 1:
                raise ValueError("Pass a single array or all multiple scalars.")

            coef = coef[0]
        super().__init__(coef)

        self.coef = coef

    def _repr_latex_(self):
        """
        Generate a LaTeX representation of the cost curve.

        Returns
        ----------
            str: LaTeX representation of the cost curve.

        Example
        ----------
            >>> cost_curve = Cost(0.5, 0.1, -0.02)
            >>> latex_repr = cost_curve._repr_latex_()
        """
        # overwrite ABCPolyBase Method to use p/q instead of x\mapsto
        # get the scaled argument string to the basis functions
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

        return rf"$q \mapsto {body}$"


    def cost(self, q):
        """
        Calculate the cost at a given quantity.

        Parameters
        ----------
            q (float): The quantity at which to calculate the cost.

        Returns
        ----------
            float: The cost at the specified quantity.

        Example
        ----------
            >>> cost_curve = Cost(0.5, 0.1, -0.02)
            >>> cost_curve.cost(10)
        """
        return self(q)

    def variable_cost(self):
        """
        Return a Cost object representing the variable cost.

        Returns
        ----------
            Cost: A Cost object representing the variable cost.

        Example
        ----------
            >>> cost_curve = Cost(0.5, 0.1, -0.02)
            >>> variable_cost_curve = cost_curve.variable_cost()
        """
        new_coef = 0, *self.coef[1:]
        return Cost(new_coef)

    def marginal_cost(self):
        """
        Return a Cost object representing the marginal cost.

        Returns
        ----------
            Cost: A Cost object representing the marginal cost.

        Example
        ----------
            >>> cost_curve = Cost(0.5, 0.1, -0.02)
            >>> marginal_cost_curve = cost_curve.marginal_cost()
        """
        new_coef = [(key+1)*c for key,c in enumerate(self.coef[1:])]
        return Cost(new_coef)

    def average_cost(self):
        """
        Return an AverageCost object representing the average cost.

        Returns
        ----------
            AverageCost: An AverageCost object representing the average cost.

        Example
        ----------
            >>> cost_curve = Cost(0.5, 0.1, -0.02)
            >>> average_cost_curve = cost_curve.average_cost()
        """
        #new_coef = [c for c in self.coef[1:]]
        return AverageCost(self.coef)


    def efficient_scale(self):
        """
        Find the quantity that minimizes average cost.

        Returns
        ----------
            float or str: The quantity that minimizes average cost or 'in prog' if it's not finite.

        Example
        ----------
            >>> cost_curve = Cost(0.5, 0.1, -0.02)
            >>> efficient_quantity = cost_curve.efficient_scale()
        """

        # Avg Cost = constant/q + linear + quadratic * q
        # d/dq Avg Cost = - constant/q**2 + quadratic = 0
        # q**2 = constant / quadratic
        coef = self.coef
        try:
            constant = coef[0]
            quad = coef[2]

            return np.sqrt(constant/quad)

        except IndexError:

            "increasing returns to scale forever"
            if constant > 0:
                return np.inf

            elif len(coef) <= 2: # linear costs
                raise ValueError('constant returns to scale')


    def breakeven_price(self):
        """
        Find the price such that economic profit is zero (perfect competition).

        Returns
        ----------
            float: The price at which economic profit is zero.

        Example
        ----------
            >>> cost_curve = Cost(0.5, 0.1, -0.02)
            >>> breakeven_price = cost_curve.breakeven_price()
        """

        # find MC = ATC
        return self.marginal_cost().cost(self.efficient_scale())

    def shutdown_price(self):
        """
        Assume perfect competition and find the price at which total revenue equals total variable cost.

        This method calculates the price at which a firm should shut down in the short run to minimize losses,
        assuming perfect competition. It finds the price at which total revenue (TR) equals total variable cost (TVC).

        Returns
        ----------
        float: The price at which total revenue equals total variable cost.

        Example
        ----------
        >>> cost_curve = Cost(0.5, 0.1, -0.02)
        >>> shutdown = cost_curve.shutdown_price()
        """

        var = self.variable_cost()
        return var.marginal_cost().cost(var.efficient_scale())



    def long_run_plot(self, ax = None):
        """
        Plot the long-run average cost (LRAC) and marginal cost (MC) curves.

        This method plots the long-run average cost (LRAC) curve and the marginal cost (MC) curve on the same graph.
        It also marks the efficient scale and the breakeven price.

        Args
        ----------
            ax (matplotlib.pyplot.axis, optional): The axis on which to plot. If not provided, the current axis is used.

        Returns
        ----------
            None

        Example
        ----------
            >>> cost_curve = Cost(0.5, 0.1, -0.02)
            >>> cost_curve.long_run_plot()
        """

        ac = self.average_cost()
        mc = self.marginal_cost()

        if ax == None:
            ax = plt.gca()

        p, q = self.breakeven_price(), self.efficient_scale()

        if q == np.inf:

            return 'in prog'

        max_q = int(2*q)
        #ac.plot(ax, label = 'LRAC', max_q = max_q)
        ax_q = np.linspace(0, max_q, 1000)
        ax_p = ac(ax_q)
        ax.plot(ax_q, ax_p, label = 'LRAC')
        mc.plot(ax, label = "MC", max_q = max_q)

        ax.plot([0,q], [p,p], linestyle = 'dashed', color = 'gray')
        ax.plot([q,q], [0,p], linestyle = 'dashed', color = 'gray')
        ax.plot([q], [p], marker = 'o')
        ax.set_xlim(0,max_q)
        ax.set_ylim(0,2*p)
        ax.legend()

    def cost_profit_plot(self, p, ax = None, items = ['tc', 'tr', 'profit']):
        """
        Plot various cost and profit components at a given price.

        This method plots the average total cost (ATC) and marginal cost (MC) curves, and it marks the given price and
        quantity on the graph. It can also shade areas to represent total cost (TC), total revenue (TR), and profit (π).

        Args
        ----------
            p (float): The price at which to evaluate the cost and profit components.
            ax (matplotlib.pyplot.axis, optional): The axis on which to plot. If not provided, the current axis is used.
            items (list of str, optional): A list of items to include in the plot. Options are 'tc', 'tr', and 'profit'.

        Returns
        ----------
            None

        Example
        ----------
            >>> cost_curve = Cost(0.5, 0.1, -0.02)
            >>> cost_curve.cost_profit_plot(0.4, items=['tc', 'tr', 'profit'])
        """
        if ax == None:
            ax = plt.gca()

        items = [str(x).lower() for x in items]

        # set p = mc
        mc = self.marginal_cost()
        q = mc.q(p)

        # plot AC and MC
        self.average_cost().plot(label = "ATC")
        mc.plot(label = "MC")


        # plot price and quantity
        ax.plot([0,q], [p,p], linestyle = 'dashed', color = 'gray')
        ax.plot([q,q], [0,p], linestyle = 'dashed', color = 'gray')
        ax.plot([q], [p], marker = 'o')


        atc_of_q = self.average_cost()(q)

        if 'profit' in items:
            # profit
            profit = q * (p - atc_of_q)
            if profit > 0:
                col = 'green'
            else:
                col = 'red'
            ax.fill_between([0,q], atc_of_q, p, color = col, alpha = 0.3, label = r"$\pi$", hatch = "\\")

        if 'tc' in items:
            # total cost
            ax.fill_between([0,q], 0, atc_of_q, facecolor = 'yellow', alpha = 0.1, label = 'TC', hatch = "/")

        if 'tr' in items:
            ax.fill_between([0,q], 0, p, facecolor = 'blue', alpha = 0.1, label = 'TR', hatch = '+')




class AverageCost:
    """
    Class representing the average cost curve.

    The average cost (AC) curve is derived from a given cost function's coefficients. It calculates the cost per unit
    of output (average cost) for different levels of output (quantity).

    Args
    ----------
        coef (array-like): Coefficients of the underlying cost function polynomial.

    Attributes
    ----------
        poly_coef (array-like): Coefficients of the underlying cost function polynomial excluding the constant term.
        coef (array-like): Coefficients of the underlying cost function polynomial, including the constant term.

    Example
    ----------
        >>> cost_curve = Cost(0.5, 0.1, -0.02)
        >>> ac_curve = AverageCost(cost_curve.coef)
    """

    def __init__(self , coef):
        """
        Initialize the AverageCost object.

        Args
        ----------
            coef (array-like): Coefficients of the underlying cost function polynomial.
        """

        self.poly_coef = coef[1:]
        self.coef = coef

    def __call__(self, q):
        """
        Calculate the average cost at a given quantity.

        Args
        ----------
            q (float): The quantity (output level) at which to calculate the average cost.

        Returns
        ----------
            float: The average cost at the given quantity.

        Example
        ----------
            >>> ac_curve = AverageCost([0.5, 0.1, -0.02])
            >>> avg_cost_at_10_units = ac_curve(10)
        """
        return Cost(self.coef)(q) / q

    def cost(self, q):
        """
        Calculate the average cost at a given quantity.

        This method is equivalent to calling the object as a function with the quantity as the argument.

        Args
        ----------
            q (float): The quantity (output level) at which to calculate the average cost.

        Returns
        ----------
            float: The average cost at the given quantity.

        Example
        ----------
            >>> ac_curve = AverageCost([0.5, 0.1, -0.02])
            >>> avg_cost_at_10_units = ac_curve.cost(10)
        """
        return self(q)

    def plot(self, ax = None, max_q = 10, label = None):
        """
        Plot the average cost curve.

        This method generates a plot of the average cost (AC) curve over a range of output levels (quantity).

        Args
        ----------
            ax (matplotlib.pyplot.axis, optional): The axis on which to plot. If not provided, the current axis is used.
            max_q (float, optional): The maximum quantity to plot up to.
            label (str, optional): Label for the curve on the plot.

        Returns
        ----------
            None

        Example
        ----------
            >>> ac_curve = AverageCost([0.5, 0.1, -0.02])
            >>> ac_curve.plot(max_q=20, label='AC Curve')
        """
        if ax == None:
            ax = plt.gca()

        xs = np.linspace(0.01, max_q, int(10*max_q))
        ys = self(xs)
        ax.plot(xs, ys, label = label)
