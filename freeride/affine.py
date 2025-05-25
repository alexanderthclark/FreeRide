import numpy as np
import matplotlib.pyplot as plt
from .base import PolyBase
from .plotting import textbook_axes

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
            x, y = "q", "p"
        elif isinstance(symbols, str):
            x, y = "q", "p"
        else:
            x, y = symbols
        self.symbols = symbols

        if slope == 0:
            if inverse:  # perfectly elastic
                self.intercept = intercept
                self.q_intercept = np.nan
                self.slope = 0

                self.inverse_expression = f"{self.intercept:g}"
                self.expression = "undefined"
                self._symbol = x  # rhs is 0*q

            else:  # perfectly inelastic
                self.q_intercept = intercept
                self.slope = np.inf
                self.intercept = np.nan

                self.inverse_expression = "undefined"
                self.expression = f"{self.q_intercept:g}"
                self._symbol = y  # rhs is 0*p
            self.coef = (self.intercept, self.slope)
            super().__init__(self.coef, symbols=symbols)
        else:
            if not inverse:
                slope, intercept = 1 / slope, -intercept / slope

            coef = (intercept, slope)
            super().__init__(coef, symbols=symbols)
            self.intercept = intercept
            self.slope = slope
            self.q_intercept = -intercept / slope
            self.inverse_expression = f"{intercept:g}{slope:+g}{x}"
            self.expression = f"{self.q_intercept:g}{1/slope:+g}{y}"

    def __call__(self, x):
        if self.slope == np.inf:
            raise Exception(f"Undefined (perfectly inelastic at {self.q_intercept})")
        else:
            return self.intercept + self.slope * x

    def __mul__(self, scalar):
        return type(self)(
            intercept=self.intercept,
            slope=self.slope * (1 / scalar),
            inverse=True,
            symbols=self.symbols,
        )

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
        # if self.slope != 0:
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
                return self.__class__(
                    new_q_intercept, 0, inverse=False, symbols=self.symbols
                )
        else:
            equiv_vert = delta * -self.slope
            new_intercept = self.intercept + equiv_vert
            # if self.slope != 0:
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
            raise ValueError("Negative price.")
        if p > self.intercept:
            raise ValueError("Price above choke price.")

        q = self.q(p)
        e = (1 / self.slope) * (p / q)
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
            raise ValueError("Negative price.")
        if (p1 > self.intercept) or (p2 > self.intercept):
            raise ValueError("Price above choke price.")

        mean_p = 0.5 * p1 + 0.5 * p2
        return self.price_elasticity(mean_p)

    def plot(self, ax=None, textbook_style=True, max_q=None, label=True, **kwargs):
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
                x2 = max_q if max_q else x1 * 2 + 1
        else:
            x1 = 0
            q_ = self.q_intercept
            if np.isnan(q_):  # if slope is 0
                q_ = 10**10
            if type(self).__name__ == "Supply":
                x2 = np.max([10, q_ * 2])
            else:
                x2 = q_

        y1 = self(x1)
        y2 = self(x2)

        xs = np.linspace(x1, x2, 2)
        ys = np.linspace(y1, y2, 2)

        if "color" not in kwargs:
            kwargs["color"] = "black"
        ax.plot(xs, ys, **kwargs)

        if textbook_style:
            textbook_axes(ax)

        if label == True:

            # Label Curves
            # if type(self).__name__ == 'Demand':
            #    x0 = self.q_intercept * .95
            # else:
            # if name:
            #    x0 = ax.get_xlim()[1] * .9
            #    y_delta = (ax.get_ylim()[1] - ax.get_ylim()[0])/30
            #    y0 = self.p(x0) + y_delta
            #    ax.text(x0, y0, name, va = 'bottom', ha = 'center', size = 14)

            # Label Axes
            ax.set_ylabel("Price")
            ax.set_xlabel("Quantity")

        ax.relim()
        ax.autoscale_view()

        return ax

    def plot_area(
        self, p, q=None, ax=None, zorder=-1, color=None, alpha=None, force=False
    ):
        """
        Plot surplus region
        """
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
            elif qstar < q0:  # plot nothing if no surplus in region
                return ax

        p01 = self.p(q[0]), self.p(q[1])

        ax.fill_between(q, p01, p, zorder=zorder, color=color, alpha=alpha)

        ax.relim()
        ax.autoscale_view()

        return ax

