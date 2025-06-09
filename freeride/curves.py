import numpy as np
import matplotlib.pyplot as plt
import warnings
from freeride.plotting import textbook_axes, AREA_FILLS, update_axes_limits
from freeride.formula import _formula
from freeride.affine import AffineElement, Affine, BaseAffine
from freeride.quadratic import QuadraticElement, BaseQuadratic
from freeride.revenue import Revenue, MarginalRevenue
from IPython.display import Latex, display
from bokeh.plotting import figure, show
from bokeh.models import HoverTool, ColumnDataSource
from freeride.exceptions import PPFError


class Demand(Affine):

    def __init__(self, intercept=None, slope=None, elements=None, inverse = True):
        """
        Initializes a Demand curve object.
        """
        super().__init__(intercept, slope, elements, inverse)
        self._check_slope()
        
        # Warn about perfectly elastic segments
        if self.has_perfectly_elastic_segment:
            warnings.warn(
                f"Created perfectly elastic demand curve. "
                f"Note: Due to current implementation limitations, this curve "
                f"cannot be used with Equilibrium or combined with other curves. "
                f"The economics are valid, but the software support is incomplete.",
                UserWarning
            )

    def _check_slope(self):
        for slope in self.slope:
            if slope > 0:
                raise Exception("Upward-sloping demand curve.")
        
        # Check for economically reasonable demand curves
        for intercept in self.intercept:
            if intercept <= 0:
                raise Exception(
                    f"Demand curve intercept must be positive (got {intercept}). "
                    f"A demand curve represents willingness to pay, so the price intercept "
                    f"should be positive."
                )
        
        if not self.has_perfectly_elastic_segment:
            if self.q(0) < 0:
                raise Exception("Negative demand.")
    
    def q(self, p):
        """
        Calculate quantity demanded at price p, handling perfectly elastic segments.
        
        For horizontal demand at price P*:
        - q(P*) = 0 (with warning about indeterminacy)
        - q(P > P*) = 0 
        - q(P < P*) = ∞
        """
        # Check if we have perfectly elastic segments
        if self.has_perfectly_elastic_segment:
            for element in self.elements:
                if element.slope == 0:  # Horizontal segment
                    p_star = element.intercept
                    if np.isclose(p, p_star):
                        warnings.warn(
                            f"Quantity demanded is indeterminate at P={p_star} for perfectly elastic demand. "
                            f"Returning np.inf as a placeholder (actual quantity is indeterminate).",
                            UserWarning
                        )
                        return np.inf
                    elif p > p_star:
                        return 0
                    else:  # p < p_star
                        return np.inf
        
        # Default behavior for non-horizontal curves
        return super().q(p)

    def consumer_surplus(self, p, q = None):
        return self.surplus(p, q)

    def total_revenue(self):
        
        return Revenue.from_demand(self)

    def marginal_revenue(self):
        
        return MarginalRevenue.from_demand(self)

    def __and__(self, other):
        """Create a Market from intersection with Supply using & operator."""
        from .equilibrium import Market
        if isinstance(other, Supply):
            return Market(demand=self, supply=other)
        else:
            return NotImplemented


class Supply(Affine):

    def __init__(self, intercept=None, slope=None, elements=None, inverse=True):
        """
        Initializes a Supply curve object.
        """
        super().__init__(intercept, slope, elements, inverse)
        self._check_slope()
        
        # Warn about perfectly elastic segments
        if self.has_perfectly_elastic_segment:
            warnings.warn(
                f"Created perfectly elastic supply curve. "
                f"Note: Due to current implementation limitations, this curve "
                f"cannot be used with Equilibrium or combined with other curves. "
                f"The economics are valid, but the software support is incomplete.",
                UserWarning
            )

    def _check_slope(self):
        for slope in self.slope:
            if slope < 0:
                raise Exception("Downward-sloping supply curve.")
        if not self.has_perfectly_elastic_segment:
            if self.q(0) < 0:
                raise Exception("Negative supply.")
    
    def q(self, p):
        """
        Calculate quantity supplied at price p, handling perfectly elastic segments.
        
        For horizontal supply at price P*:
        - q(P*) = 0 (with warning about indeterminacy)
        - q(P > P*) = ∞ 
        - q(P < P*) = 0
        """
        # Check if we have perfectly elastic segments
        if self.has_perfectly_elastic_segment:
            for element in self.elements:
                if element.slope == 0:  # Horizontal segment
                    p_star = element.intercept
                    if np.isclose(p, p_star):
                        warnings.warn(
                            f"Quantity supplied is indeterminate at P={p_star} for perfectly elastic supply. "
                            f"Returning np.inf as a placeholder (actual quantity is indeterminate).",
                            UserWarning
                        )
                        return np.inf
                    elif p > p_star:
                        return np.inf
                    else:  # p < p_star
                        return 0
        
        # Default behavior for non-horizontal curves
        return super().q(p)

    def producer_surplus(self, p, q = None):
        return -self.surplus(p, q)
    
    def __and__(self, other):
        """Create a Market from intersection with Demand using & operator."""
        from .equilibrium import Market
        if isinstance(other, Demand):
            return Market(demand=other, supply=self)
        else:
            return NotImplemented


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
        self._check_slope()
        self.pieces = ppf_sum(*self.elements)


    def _check_slope(self):
        for slope in self.slope:
            if slope >= 0 or np.isinf(slope):
                raise PPFError("Upward-sloping or infinite-slope PPF.")


    def __add__(self, other):
        elements = self.elements + other.elements
        return type(self)(elements=elements)

    def __call__(self, x):
        """Return the quantity of the second good for ``x`` units of the first."""
        for piece in self.pieces:
            if piece:
                a, b = piece._domain
                if (a <= x <= b) or (a >= x >= b):
                    return piece(x)
        return np.nan

    def horizontal_shift(self, delta, inplace=True):
        new_elements = [e.horizontal_shift(delta, inplace=False) for e in self.elements]
        if inplace:
            self.__init__(elements=new_elements)
            return self
        return type(self)(elements=new_elements)

    def vertical_shift(self, delta, inplace=True):
        new_elements = [e.vertical_shift(delta, inplace=False) for e in self.elements]
        if inplace:
            self.__init__(elements=new_elements)
            return self
        return type(self)(elements=new_elements)

    def __mul__(self, scalar):
        new_elements = []
        for e in self.elements:
            new_intercept = scalar * e.intercept
            new_el = AffineElement(
                intercept=new_intercept,
                slope=e.slope,
                inverse=True,
                symbols=e.symbols,
            )
            new_elements.append(new_el)
        return type(self)(elements=new_elements)

    def __rmul__(self, scalar):
        return self.__mul__(scalar)

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

            update_axes_limits(ax)

            return ax


