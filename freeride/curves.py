import numpy as np
import matplotlib.pyplot as plt
from freeride.plotting import textbook_axes, AREA_FILLS
from freeride.formula import _formula
from freeride.base import QuadraticElement, AffineElement, BaseQuadratic
from IPython.display import Latex, display
from bokeh.plotting import figure, show
from bokeh.models import HoverTool, ColumnDataSource
from freeride.exceptions import PPFError



def intersection(element1, element2):
    """Return the intersection of two affine elements.

    The result is a 1D array ``[p, q]`` giving the price and quantity at the
    intersection.  When either line is perfectly vertical (``slope == np.inf``)
    or perfectly horizontal (``slope == 0``) the intersection is computed
    directly.  If both lines are vertical or both horizontal, a
    ``LinAlgError`` is raised.

    Parameters
    ----------
    element1, element2 : :class:`AffineElement`
        Lines for which to compute the intersection.

    Returns
    -------
    numpy.ndarray
        ``[p, q]`` of the intersection point.

    Raises
    ------
    numpy.linalg.LinAlgError
        If the lines are parallel.

    Examples
    --------
    >>> line1 = AffineElement(intercept=12, slope=-1)
    >>> line2 = AffineElement(intercept=0, slope=2)
    >>> intersection(line1, line2)
    array([8., 4.])
    """

    # Parallel vertical or horizontal lines
    if (element1.slope == np.inf and element2.slope == np.inf) or (
        element1.slope == 0 and element2.slope == 0
    ):
        raise np.linalg.LinAlgError("Lines are parallel")

    # Handle a vertical line (perfectly inelastic)
    if element1.slope == np.inf:
        q = element1.q_intercept
        p = element2(q)
        return np.array([p, q])
    if element2.slope == np.inf:
        q = element2.q_intercept
        p = element1(q)
        return np.array([p, q])

    # Handle a horizontal line (perfectly elastic)
    if element1.slope == 0:
        p = element1.intercept
        q = element2.q(p)
        return np.array([p, q])
    if element2.slope == 0:
        p = element2.intercept
        q = element1.q(p)
        return np.array([p, q])

    # Generic case
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
    """Combine production possibilities frontiers.

    Parameters
    ----------
    *curves : sequence of :class:`AffineElement`
        PPF curves to aggregate.
    comparative_advantage : bool, optional
        When ``True`` curves are ordered by slope from steepest to
        flattest before summation, highlighting comparative advantage.

    Returns
    -------
    list of :class:`AffineElement`
        The shifted and vertically stacked PPF segments forming the
        aggregate frontier.
    """

    slope_and_curves = sorted([(s.slope, s) for s in curves], reverse=comparative_advantage)
    curves = [t[1] for t in slope_and_curves]
    x_intercepts = [c.q_intercept for c in curves]
    y_intercepts = [c.intercept for c in curves]

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

    def __bool__(self):
        return bool(np.any([bool(el) for el in self.elements]))

    def _has_perfectly_elastic_segment(self):
        """Return ``True`` if any element is perfectly elastic (zero slope)."""
        return any(el.slope == 0 for el in self.elements)

    def _has_perfectly_inelastic_segment(self):
        """Return ``True`` if any element is perfectly inelastic (infinite slope)."""
        return any(np.isinf(el.slope) for el in self.elements)

    @property
    def has_perfectly_elastic_segment(self):
        """bool: Whether the curve contains a perfectly elastic segment."""
        return self._has_perfectly_elastic_segment()

    @property
    def has_perfectly_inelastic_segment(self):
        """bool: Whether the curve contains a perfectly inelastic segment."""
        return self._has_perfectly_inelastic_segment()

    @property
    def has_perfect_segment(self):
        """bool: Whether the curve contains a perfectly elastic or inelastic segment."""
        return self.has_perfectly_elastic_segment or self.has_perfectly_inelastic_segment

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
            return type(self)(elements=new_elements)

    def vertical_shift(self, delta, inplace=True):
        new_elements = [e.vertical_shift(delta, inplace=False) for e in self.elements]
        if inplace:
            self.__init__(elements=new_elements)
        else:
            return type(self)(elements=new_elements)

    @property
    def q_intercept(self):
        """Return the quantity intercept(s) for the affine elements."""
        q_int = [-b / m for b, m in zip(self.intercept, self.slope)]
        return q_int[0] if len(q_int) == 1 else q_int


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

    def __mul__(self, scalar):
        elements = [e*scalar for e in self.elements]
        return type(self)(elements=elements)
    
    def __rmul__(self, scalar):
        elements = [e*scalar for e in self.elements]
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
        label : bool, optional
            Whether to add curve/axis labels. Default True.
        **kwargs : dict
            Additional keyword arguments for controlling line color, style, etc.

        Returns
        -------
        ax : matplotlib.axes.Axes
        '''

        def safe_eval(x):
            # Evaluate self(x) or return np.nan if out of domain or invalid
            try:
                val = self.__call__(x)
                if np.isfinite(val):
                    return val
                else:
                    return np.nan
            except:
                return np.nan

        if ax is None:
            fig, ax = plt.subplots()

        # Plot each piece in self.pieces
        param_names = ['color', 'linewidth', 'linestyle', 'lw', 'ls']
        plot_dict = {key: kwargs[key] for key in kwargs if key in param_names}
        for piece in self.pieces:
            if piece:
                piece.plot(ax=ax, label=label, max_q=max_q, **plot_dict)

        if set_lims:
            ax.relim()
            ax.autoscale_view()

        # Apply any leftover kwargs that might be e.g. title, xlim, ylim
        for key, value in kwargs.items():
            if hasattr(plt, key):
                plt_function = getattr(plt, key)
                if callable(plt_function):
                    if isinstance(value, (tuple, list)):
                        plt_function(*value)
                    else:
                        plt_function(value)

        # Simple labeling
        if label:
            ax.set_xlabel("Quantity")
            ax.set_ylabel("Price")

        return ax

    def plot_surplus(self, p, q=None, ax=None, color=None, max_q=None, alpha=None):

        if (color is None) and isinstance(self, Supply):
            color = AREA_FILLS[1]
        elif color is None:
            color = AREA_FILLS[0]

        if ax is None:
            ax = self.plot(max_q=max_q)
        for piece in self.pieces:
            if piece:
                piece.plot_area(p,
                             q=q,
                             ax=ax,
                             color=color,
                             alpha=alpha)

        ax.relim()
        ax.autoscale_view()

        return ax

    def surplus(self, p, q=None):
        '''
        Returns surplus area. The areas are negative for producer surplus.
        '''
        if q is None:
            q = self.q(p)

        if q > 0:

            # find inframarginal surplus
            trapezoids = [piece for piece in self.pieces if piece and (np.max(piece._domain) < q)]
            trap_areas = [piece._domain_length*(np.mean([piece.p(piece._domain[0]),piece.p(piece._domain[1])])-p) for piece in trapezoids]


            # find the last unit demanded and get surplus from that curve
            last_piece = self._get_active_piece(q)
            q0 = np.min(last_piece._domain)
            base = q - q0
            ht1 = last_piece.p(q0) - p
            ht2 = last_piece.p(q) - p
            area = base * 0.5 * (ht1 + ht2)

            return area + np.sum(trap_areas)

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
        if not self.has_perfectly_elastic_segment:
            if self.q(0) < 0:
                raise Exception("Negative demand.")

    def consumer_surplus(self, p, q = None):
        return self.surplus(p, q)

    def total_revenue(self):
        
        elements = list()
        pieces = [p for p in self.pieces if p]
        for piece in pieces:
            coef = 0, piece.intercept, piece.slope
            revenue_element = QuadraticElement(*coef)
            revenue_element._domain = sorted(piece._domain)
            elements.append(revenue_element)
            
        return BaseQuadratic(elements=elements)


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
                raise Exception("Downward-sloping supply curve.")
        if not self.has_perfectly_elastic_segment:
            if self.q(0) < 0:
                raise Exception("Negative supply.")

    def producer_surplus(self, p, q = None):
        return -self.surplus(p, q)


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

            ax.relim()
            ax.autoscale_view()

            return ax


