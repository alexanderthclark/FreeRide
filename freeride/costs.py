import numpy as np
import matplotlib.pyplot as plt
import numbers
from freeride.plotting import textbook_axes
from freeride.curves import *


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
            parens = False
        elif scale == 1:
            term = f"{self._repr_latex_scalar(off)} + q"
            parens = True
        elif off == 0:
            term = f"{self._repr_latex_scalar(scale)}q"
            parens = True
        else:
            term = (
                f"{self._repr_latex_scalar(off)} + "
                f"{self._repr_latex_scalar(scale)}q"
            )
            parens = True

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
            term_str = self._repr_latex_term(i, term, parens)
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
