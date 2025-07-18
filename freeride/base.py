"""Base class for polynomial functions used in FreeRide."""

import numbers
from collections.abc import Iterable

import matplotlib.pyplot as plt
import numpy as np

from freeride.plotting import textbook_axes, update_axes_limits


class PolyBase(np.polynomial.Polynomial):
    """Polynomial base class using ``q`` and ``p`` as variables.

    Extends :class:`numpy.polynomial.Polynomial` with economics-oriented
    helpers.

    .. math::

       p = \sum_{k=0}^n c_k q^k

    Parameters
    ----------
    *coef : array-like or scalar
        Polynomial coefficients.

    Attributes
    ----------
    coef : ndarray
        Stored coefficients.

    Examples
    --------
    >>> poly = PolyBase([1, -2, 1])  # x^2 - 2x + 1
    >>> poly.p(2.0)
    1.0
    """

    def __init__(self, *coef, symbols=None, domain=None):
        """Initialize the polynomial.

        Parameters
        ----------
        *coef : array-like or scalar
            Polynomial coefficients.
        symbols : tuple[str, str] | str | None, optional
            Variable names. Defaults to ``("q", "p")``.
        domain : tuple[float, float] | None, optional
            Closed interval for evaluation.
        """
        self.set_symbols(symbols)
        self.is_undefined = coef == ([],)  # helpful in sum functions
        if not self.is_undefined:
            coef = np.squeeze(np.array(coef, ndmin=1))
            super().__init__(coef, domain=None, symbol=self._symbol)
        else:
            self.coef = []
            self._symbol = self.x
        # user-defined domain for building piecewise functions
        self._domain = domain

    def in_domain(self, x):
        """Test if value is in the domain using [a,b] convention (closed interval)."""
        if self._domain:
            d = sorted(self._domain)
            return d[0] <= x <= d[1]
        else:
            return True

    def __call__(self, x):
        if isinstance(x, Iterable):
            return [self.__call__(i) for i in x]
        if self.is_undefined:
            raise ValueError("Polynomial is undefined.")
        elif self.in_domain(x):
            return super().__call__(x)
        else:
            raise ValueError(
                f"{self.x}={x} is outside of the function domain, {self._domain}."
            )

    def __bool__(self):
        return not self.is_undefined

    def set_symbols(self, symbols):
        self.symbols = symbols
        if isinstance(symbols, str):
            x = symbols
            y = None
        elif symbols is None:
            x, y = "q", "p"
        elif len(symbols) == 2:
            x, y = symbols
        else:
            raise ValueError("symbols not properly set")
        self.x, self.y = x, y
        self.symbols = self.x, self.y
        self._symbol = self.x

    def p(self, q: float):
        """Return price at quantity ``q``.

        Parameters
        ----------
        q : float
            Quantity value.

        Returns
        -------
        float
            Price.
        """
        return self.__call__(q)

    def q(self, p):
        """Return the quantity at price ``p``.

        Parameters
        ----------
        p : float
            Price value.

        Returns
        -------
        float | ndarray
            Quantity or array of quantities.
        """
        # Perfectly Inelastic
        if self.slope == np.inf:
            return self.q_intercept

        coef2 = (self.coef[0] - p, *self.coef[1:])[::-1]
        roots = np.roots(coef2)

        if roots.shape == (1,):
            return roots[0]
        else:
            return roots

    def plot(
        self, ax=None, label=None, max_q=100, min_plotted_q=0, textbook_style=True
    ):
        """Plot the polynomial.

        Parameters
        ----------
        ax : matplotlib.axes.Axes, optional
            Target axes. Defaults to ``matplotlib.pyplot.gca()``.
        label : str, optional
            Legend label.
        max_q : float, optional
            Upper bound on quantity (default ``100``).
        min_plotted_q : float, optional
            Minimum quantity to plot.
        textbook_style : bool, optional
            Apply textbook-style axis formatting.
        """
        if ax is None:
            ax = plt.gca()

        x_vals = np.linspace(0, max_q, max_q * 5 + 1)
        x_vals = x_vals[x_vals >= min_plotted_q]
        y_vals = self(x_vals)

        ax.plot(x_vals, y_vals, label=label)

        if textbook_style:
            textbook_axes(ax)

        update_axes_limits(ax)

    # Similar to numpy ABCPolyBase
    def _repr_latex_(self):
        """Return a LaTeX representation of the polynomial."""
        # overwrite ABCPolyBase Method to use p/q instead of x\mapsto
        # get the scaled argument string to the basis functions
        if hasattr(self, "is_undefined") and self.is_undefined:
            return "Undefined"
        elif (
            hasattr(self, "inverse_expression")
            and self.inverse_expression != "undefined"
        ):
            latex_str = f"{self.y}={self.inverse_expression}"
            return rf"${latex_str}$"
        elif hasattr(self, "expression") and self.expression != "undefined":
            latex_str = f"{self.y}={self.expression}"
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
            if term_str == "1":
                part = coef_str
            else:
                part = rf"{coef_str}\,{term_str}"

            if c == 0:
                part = mute(part)

            parts.append(part)

        if parts:
            body = "".join(parts)
        else:
            # in case somehow there are no coefficients at all
            body = "0"
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
