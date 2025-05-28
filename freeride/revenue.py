from __future__ import annotations

"""Revenue curve utilities for microeconomic analysis.

This module provides classes for representing and analyzing total revenue
and marginal revenue curves, which are fundamental concepts in microeconomics
and particularly important for monopoly analysis.
"""

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
    
    def __repr__(self):
        """Return string representation of the revenue curve."""
        if len(self.elements) == 1:
            el = self.elements[0]
            # Format as TR = aQ + bQ²
            parts = []
            if el.intercept != 0:
                parts.append(f"{el.intercept}")
            if el.linear_coef != 0:
                if el.linear_coef == 1:
                    parts.append("Q")
                elif el.linear_coef == -1:
                    parts.append("-Q")
                else:
                    parts.append(f"{el.linear_coef}Q")
            if el.quadratic_coef != 0:
                if el.quadratic_coef == 1:
                    parts.append("Q²")
                elif el.quadratic_coef == -1:
                    parts.append("-Q²")
                else:
                    parts.append(f"{el.quadratic_coef}Q²")
            
            if parts:
                expr = " + ".join(parts).replace(" + -", " - ")
                return f"Revenue: TR = {expr}"
            else:
                return "Revenue: TR = 0"
        else:
            return f"Revenue: Piecewise quadratic with {len(self.elements)} segments"
    
    def __str__(self):
        """Return string representation."""
        return self.__repr__()
    
    def _repr_latex_(self):
        """Return LaTeX representation for Jupyter notebooks."""
        if len(self.elements) == 1:
            el = self.elements[0]
            # Build LaTeX expression
            parts = []
            if el.intercept != 0:
                parts.append(str(el.intercept))
            if el.linear_coef != 0:
                if el.linear_coef == 1:
                    parts.append("Q")
                elif el.linear_coef == -1:
                    parts.append("-Q")
                else:
                    parts.append(f"{el.linear_coef}Q")
            if el.quadratic_coef != 0:
                if el.quadratic_coef == 1:
                    parts.append("Q^2")
                elif el.quadratic_coef == -1:
                    parts.append("-Q^2")
                else:
                    parts.append(f"{el.quadratic_coef}Q^2")
            
            if parts:
                expr = " + ".join(parts).replace(" + -", " - ")
                return f"$$TR = {expr}$$"
            else:
                return "$$TR = 0$$"
        else:
            # Piecewise representation
            lines = ["$$TR = \\begin{cases}"]
            for el in self.elements:
                parts = []
                if el.intercept != 0:
                    parts.append(str(el.intercept))
                if el.linear_coef != 0:
                    coef_str = "" if el.linear_coef == 1 else "-" if el.linear_coef == -1 else str(el.linear_coef)
                    parts.append(f"{coef_str}Q")
                if el.quadratic_coef != 0:
                    coef_str = "" if el.quadratic_coef == 1 else "-" if el.quadratic_coef == -1 else str(el.quadratic_coef)
                    parts.append(f"{coef_str}Q^2")
                
                expr = " + ".join(parts).replace(" + -", " - ") if parts else "0"
                if el._domain:
                    domain_str = f"{el._domain[0]} \\leq Q \\leq {el._domain[1]}"
                else:
                    domain_str = "Q \\geq 0"
                lines.append(f"{expr} & \\text{{if }} {domain_str} \\\\")
            lines.append("\\end{cases}$$")
            return "\n".join(lines)

    @classmethod
    def from_demand(cls, demand) -> "Revenue":
        """Construct a Revenue curve from a :class:`Demand` instance.
        
        Total revenue is calculated as TR(Q) = P(Q) * Q, where P(Q) is the
        inverse demand function. For a linear demand P = a - bQ, this gives
        TR = aQ - bQ².
        
        Parameters
        ----------
        demand : Demand
            The demand curve to convert to revenue.
            
        Returns
        -------
        Revenue
            The total revenue curve.
            
        Examples
        --------
        >>> from freeride import Demand
        >>> demand = Demand(10, -2)  # P = 10 - 2Q
        >>> revenue = Revenue.from_demand(demand)
        >>> revenue
        Revenue: TR = 10Q - 2Q²
        """
        elements = []
        pieces = [p for p in demand.pieces if p]
        for piece in pieces:
            # TR = P*Q = (a + bQ)*Q = aQ + bQ²
            coef = 0, piece.intercept, piece.slope
            revenue_element = QuadraticElement(*coef)
            revenue_element._domain = sorted(piece._domain) if piece._domain else None
            elements.append(revenue_element)
        return cls(elements=elements)

    def marginal_revenue(self) -> "MarginalRevenue":
        """Return the marginal revenue curve.
        
        Marginal revenue is the derivative of total revenue with respect
        to quantity: MR(Q) = d(TR)/dQ. For a quadratic TR = aQ + bQ²,
        this gives MR = a + 2bQ.
        
        Returns
        -------
        MarginalRevenue
            The marginal revenue curve.
            
        Examples
        --------
        >>> from freeride import Demand
        >>> demand = Demand(10, -2)  # P = 10 - 2Q
        >>> revenue = demand.total_revenue()
        >>> mr = revenue.marginal_revenue()
        >>> mr
        MarginalRevenue: MR = 10 - 4Q
        """
        return MarginalRevenue.from_revenue(self)

    def plot(self, ax=None, max_q=10, label=None, **kwargs):
        """Plot the total revenue curve.
        
        Parameters
        ----------
        ax : matplotlib.axes.Axes, optional
            The axes on which to draw. If None, uses current axes.
        max_q : float, optional
            Maximum quantity to plot. Default is 10.
        label : str, optional
            Label for the curve in the legend.
        **kwargs
            Additional keyword arguments passed to matplotlib plot.
            
        Returns
        -------
        matplotlib.axes.Axes
            The axes containing the plot.
        """
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
    """Piecewise linear marginal revenue curve.
    
    Marginal revenue represents the additional revenue from selling one more
    unit. For linear demand curves, MR has the same intercept but twice the
    slope of the demand curve.
    
    Attributes
    ----------
    elements : list of AffineElement
        The piecewise linear segments of the MR curve.
    """

    def __init__(self, elements):
        self.elements = elements
    
    def __repr__(self):
        """Return string representation of the marginal revenue curve."""
        if len(self.elements) == 1:
            el = self.elements[0]
            # Format as MR = a + bQ
            parts = []
            if el.intercept != 0:
                parts.append(f"{el.intercept}")
            if el.slope != 0:
                if el.slope == 1:
                    parts.append("Q")
                elif el.slope == -1:
                    parts.append("-Q")
                else:
                    parts.append(f"{el.slope}Q")
            
            if parts:
                expr = " + ".join(parts).replace(" + -", " - ")
                return f"MarginalRevenue: MR = {expr}"
            else:
                return "MarginalRevenue: MR = 0"
        else:
            return f"MarginalRevenue: Piecewise linear with {len(self.elements)} segments"
    
    def __str__(self):
        """Return string representation."""
        return self.__repr__()
    
    def _repr_latex_(self):
        """Return LaTeX representation for Jupyter notebooks."""
        if len(self.elements) == 1:
            el = self.elements[0]
            # Build LaTeX expression
            parts = []
            if el.intercept != 0:
                parts.append(str(el.intercept))
            if el.slope != 0:
                if el.slope == 1:
                    parts.append("Q")
                elif el.slope == -1:
                    parts.append("-Q")
                else:
                    parts.append(f"{el.slope}Q")
            
            if parts:
                expr = " + ".join(parts).replace(" + -", " - ")
                return f"$$MR = {expr}$$"
            else:
                return "$$MR = 0$$"
        else:
            # Piecewise representation
            lines = ["$$MR = \\begin{cases}"]
            for el in self.elements:
                parts = []
                if el.intercept != 0:
                    parts.append(str(el.intercept))
                if el.slope != 0:
                    coef_str = "" if el.slope == 1 else "-" if el.slope == -1 else str(el.slope)
                    parts.append(f"{coef_str}Q")
                
                expr = " + ".join(parts).replace(" + -", " - ") if parts else "0"
                if el._domain:
                    domain_str = f"{el._domain[0]} \\leq Q \\leq {el._domain[1]}"
                else:
                    domain_str = "Q \\geq 0"
                lines.append(f"{expr} & \\text{{if }} {domain_str} \\\\")
            lines.append("\\end{cases}$$")
            return "\n".join(lines)

    def __call__(self, q: float) -> float:
        """Evaluate marginal revenue at quantity q.
        
        Parameters
        ----------
        q : float
            The quantity at which to evaluate MR.
            
        Returns
        -------
        float
            The marginal revenue at quantity q.
            
        Examples
        --------
        >>> from freeride import Demand
        >>> demand = Demand(10, -2)
        >>> mr = demand.total_revenue().marginal_revenue()
        >>> mr(2)  # MR at Q=2
        2.0
        """
        for el in self.elements:
            dom = el._domain
            if dom is None or (min(dom) <= q <= max(dom)):
                return el(q)
        return 0.0

    @classmethod
    def from_revenue(cls, revenue: Revenue) -> "MarginalRevenue":
        """Construct marginal revenue from a total revenue curve.
        
        Takes the derivative of the revenue function with respect to quantity.
        For TR = aQ + bQ², this gives MR = a + 2bQ.
        
        Parameters
        ----------
        revenue : Revenue
            The total revenue curve to differentiate.
            
        Returns
        -------
        MarginalRevenue
            The marginal revenue curve.
        """
        elements = []
        for piece in revenue.elements:
            if piece:
                # MR = d(TR)/dQ = d(aQ + bQ²)/dQ = a + 2bQ
                intercept = piece.linear_coef
                slope = 2 * piece.quadratic_coef
                el = AffineElement(intercept, slope, inverse=True)
                el._domain = piece._domain
                elements.append(el)
        return cls(elements)

    def plot(self, ax=None, max_q=10, label=None):
        """Plot the marginal revenue curve.
        
        Parameters
        ----------
        ax : matplotlib.axes.Axes, optional
            The axes on which to draw. If None, uses current axes.
        max_q : float, optional  
            Maximum quantity to plot. Default is 10.
        label : str, optional
            Label for the curve in the legend.
            
        Returns
        -------
        matplotlib.axes.Axes
            The axes containing the plot.
        """
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

