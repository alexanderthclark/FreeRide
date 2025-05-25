import numpy as np
import matplotlib.pyplot as plt
from .base import PolyBase
from .plotting import textbook_axes
from .formula import _quadratic_formula

class QuadraticElement(PolyBase):
    """
    Extends the PolyBase class and represents a quadratic function used in revenue and cost curves.
    """

    def __init__(
        self, intercept, linear_coef, quadratic_coef, symbols=None, domain=None
    ):
        """
        Initialize QuadraticElement class.
        """

        if symbols is None:
            symbols = "q"
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
        new_intercept = a - b * delta + c * delta**2
        new_linear_coef = b - 2 * c * delta
        new_quadratic_coef = c
        coef = new_intercept, new_linear_coef, new_quadratic_coef
        if inplace:
            self.__init__(*coef, symbols=self.symbols)
        else:
            return self.__class__(*coef, symbols=self.symbols)

    def plot(self, ax=None, textbook_style=True, max_q=100, label=True, **kwargs):
        """Plot the quadratic element.

        Parameters
        ----------
        ax : matplotlib.axes.Axes, optional
            Axis on which to draw. Created automatically if omitted.
        textbook_style : bool, optional
            If ``True`` the axes are formatted with :func:`textbook_axes`.
        max_q : float, optional
            Upper bound for the quantity range when no domain is specified.
        label : bool, optional
            When ``True`` add basic axis labels.
        **kwargs : dict
            Additional ``matplotlib`` styling options passed to ``plot``.
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

        if "color" not in kwargs:
            kwargs["color"] = "black"
        ax.plot(xs, ys, **kwargs)

        if textbook_style:
            textbook_axes(ax)

        if label == True:
            # ax.set_ylabel("Price")
            ax.set_xlabel("Quantity")

        ax.relim()
        ax.autoscale_view()

        return ax

    def plot_area_below(self, q0, q1, ax=None, zorder=-1, color=None, alpha=None):
        """
        Plot surplus region
        """
        if ax is None:
            ax = self.plot()

        xs = np.linspace(q0, q1, 100)
        ys = self(xs)
        ax.fill_between(xs, 0, ys, zorder=zorder, color=color, alpha=alpha)

        ax.relim()
        ax.autoscale_view()

        return ax

    def plot_area_above(self, q0, q1, y, ax=None, zorder=-1, color=None, alpha=None):
        """
        Plot surplus region
        """
        if ax is None:
            ax = self.plot()

        xs = np.linspace(q0, q1, 100)
        ys = self(xs)
        ax.fill_between(xs, ys, y, zorder=zorder, color=color, alpha=alpha)

        ax.relim()
        ax.autoscale_view()

        return ax

    @classmethod
    def from_formula(cls, equation: str):
        a, b, c = _quadratic_formula(equation)
        return cls(c, b, a, domain=(-np.inf, np.inf))


class BaseQuadratic:
    """General piecewise quadratic objects."""

    def __init__(self, intercept=None, linear_coef=None, quadratic_coef=None, elements=None):
        """Create a piecewise quadratic curve."""
        if elements is None:
            if isinstance(linear_coef, (int, float)):
                linear_coef = [linear_coef]
            if isinstance(intercept, (int, float)):
                intercept = [intercept]
            if isinstance(quadratic_coef, (int, float)):
                quadratic_coef = [quadratic_coef]
            if (len(quadratic_coef) != len(intercept)) or (len(linear_coef) != len(intercept)):
                raise ValueError("Coefficient lengths do not match.")

            zipped = zip(intercept, linear_coef, quadratic_coef)
            elements = [QuadraticElement(*coef) for coef in zipped]
        self.elements = elements

        if intercept is None:
            intercept = [c.intercept for c in elements]
        if linear_coef is None:
            linear_coef = [c.linear_coef for c in elements]
        if quadratic_coef is None:
            quadratic_coef = [c.quadratic_coef for c in elements]

        self.intercept = intercept
        self.linear_coef = linear_coef
        self.quadratic_coef = quadratic_coef

    @classmethod
    def from_points(cls, xy_points, fit=False):
        """Creates a Quadratic object from points."""
        x = [i[0] for i in xy_points]
        y = [i[1] for i in xy_points]
        if fit:
            coef = np.polyfit(x, y, 2)
        else:
            A_array = [[qp[0]**2, qp[0], 1] for qp in xy_points]
            p_vals = [qp[1] for qp in xy_points]

            A = np.array(A_array)
            b = np.array(p_vals)
            coef = np.linalg.solve(A, b)

        quad, lin, constant = tuple(coef)
        return cls(constant, lin, quad)

    @classmethod
    def from_formula(cls, equation: str):
        element = QuadraticElement.from_formula(equation)
        return cls(elements=[element])

    def horizontal_shift(self, delta, inplace=True):
        new_elements = [e.horizontal_shift(delta, inplace=False) for e in self.elements]
        if inplace:
            self.__init__(elements=new_elements)
        else:
            return self.__class__(elements=new_elements)

    def vertical_shift(self, delta, inplace=True):
        new_elements = [e.vertical_shift(delta, inplace=False) for e in self.elements]
        if inplace:
            self.__init__(elements=new_elements)
        else:
            return self.__class__(elements=new_elements)

    def plot(self, ax=None, set_lims=True, max_q=None, label=True, **kwargs):
        """Plot the quadratic curve."""
        if ax is None:
            fig, ax = plt.subplots()

        param_names = ['color', 'linewidth', 'linestyle', 'lw', 'ls']
        plot_dict = {key: kwargs[key] for key in kwargs if key in param_names}
        for elmt in self.elements:
            if elmt:
                elmt.plot(ax=ax, label=label, max_q=max_q, **plot_dict)

        if set_lims:
            ax.relim()
            ax.autoscale_view()

        return ax

    def active_element(self, q):
        for piece in self.elements:
            domain = piece._domain
            if domain is None or (np.min(domain) <= q <= np.max(domain)):
                return piece
        return None

    def __call__(self, q):
        element = self.active_element(q)
        if element:
            return element(q)
        else:
            return 0
