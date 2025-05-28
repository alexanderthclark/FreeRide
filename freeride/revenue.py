from __future__ import annotations

"""Revenue curve utilities."""

import numpy as np
import matplotlib.pyplot as plt

from .quadratic import QuadraticElement, BaseQuadratic
from .affine import AffineElement
from .plotting import update_axes_limits


class Revenue(BaseQuadratic):
    """Piecewise quadratic revenue curve.

    This class represents total revenue as a function of quantity. It is
    typically generated from a :class:`~freeride.curves.Demand` curve and
    inherits all functionality of :class:`~freeride.quadratic.BaseQuadratic`.
    """

    @classmethod
    def from_demand(cls, demand) -> "Revenue":
        """Construct a Revenue curve from a :class:`Demand` instance."""
        elements = []
        pieces = [p for p in demand.pieces if p]
        for piece in pieces:
            coef = 0, piece.intercept, piece.slope
            revenue_element = QuadraticElement(*coef)
            revenue_element._domain = sorted(piece._domain)
            elements.append(revenue_element)
        return cls(elements=elements)

    def marginal_revenue(self) -> "MarginalRevenue":
        """Return the marginal revenue curve."""
        return MarginalRevenue.from_revenue(self)

    def plot(self, ax=None, max_q=10, label=None, **kwargs):
        """Plot the total revenue curve."""
        if ax is None:
            ax = plt.gca()

        for el in self.elements:
            if el:
                if el._domain:
                    x1, x2 = el._domain
                else:
                    x1, x2 = 0, max_q
                if max_q is not None:
                    x2 = min(x2, max_q)
                xs = np.linspace(x1, x2, int(50 * max_q))
                ys = el.intercept + el.linear_coef * xs + el.quadratic_coef * xs ** 2
                ax.plot(xs, ys, **kwargs)

        if label:
            ax.lines[-1].set_label(label)
            ax.legend()

        ax.set_xlabel("Quantity")
        ax.set_ylabel("Total Revenue")

        update_axes_limits(ax)

        return ax


class MarginalRevenue:
    """Piecewise linear marginal revenue curve."""

    def __init__(self, elements):
        self.elements = elements

    def __call__(self, q: float) -> float:
        for el in self.elements:
            dom = el._domain
            if dom is None or (min(dom) <= q <= max(dom)):
                return el(q)
        return 0.0

    @classmethod
    def from_revenue(cls, revenue: Revenue) -> "MarginalRevenue":
        elements = []
        for piece in revenue.elements:
            if piece:
                intercept = piece.linear_coef
                slope = 2 * piece.quadratic_coef
                el = AffineElement(intercept, slope, inverse=True)
                el._domain = piece._domain
                elements.append(el)
        return cls(elements)

    def plot(self, ax=None, max_q=10, label=None):
        if ax is None:
            ax = plt.gca()

        for el in self.elements:
            if el:
                el.plot(ax=ax, max_q=max_q, label=False)

        if label:
            for line in ax.get_lines()[-len(self.elements):]:
                line.set_label(label)
            ax.legend()

        ax.set_xlabel("Quantity")
        ax.set_ylabel("Marginal Revenue")

        update_axes_limits(ax)

        return ax

