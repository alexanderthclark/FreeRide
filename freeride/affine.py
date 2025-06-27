import numpy as np
import matplotlib.pyplot as plt
from .base import PolyBase
from .plotting import textbook_axes, AREA_FILLS, update_axes_limits
from freeride.formula import _formula
from IPython.display import Latex, display


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
        The parameters can be interpreted as inverse slope and intercept if the
        `inverse` parameter is True.

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

        This method shifts the supply or demand curve vertically by the specified
        amount `delta`.
        A positive `delta` shifts the demand curve to the right. A negative
        `delta` shifts the supply curve to the left.

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
        ----------
        ax : matplotlib.axes._axes.Axes, optional
            The matplotlib axis to use for plotting. If not provided, the current
            axes will be used or a new figure will be created.
        textbook_style : bool, optional
            If True, use textbook-style plot formatting with clean axes and
            appropriate labels. Defaults to True.
        max_q : float, optional
            The maximum quantity value for the plot. If not specified, a sensible
            default will be calculated based on the curve's intercepts.
        label : bool, optional
            If True, label the curve and axes. Defaults to True.
        **kwargs : dict
            Additional keyword arguments passed to matplotlib's plot function.
            Common options include:
            - color : str, default 'black'
            - linewidth : int, default 2
            - linestyle : str, default '-'
            - alpha : float, default 1.0

        Returns
        -------
        matplotlib.axes._axes.Axes
            The axes object containing the plot, which can be further customized.

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

        update_axes_limits(ax)

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

        update_axes_limits(ax)

        return ax

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

    def __init__(self, intercept=None, slope=None, elements=None, inverse=True, sum_elements=True):
        """
        Initialize the BaseAffine object.

        Parameters
        ----------
        intercept : float or list of floats, optional
            The intercept(s) of the affine transformation. Default is None.
        slope : float or list of floats, optional
            The slope(s) of the affine transformation. Default is None.
        elements : list of AffineElement, optional
            List of AffineElement objects. If provided, it overrides
            `intercept` and `slope`. Default is None.
        inverse : bool, optional
            Indicates if the transformation should be inverted. Default is True.
        sum_elements : bool, optional
            Whether to sum elements together (True) or keep them as separate
            pieces (False). Default is True.

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
        self.sum_elements = sum_elements

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

    def __init__(self, intercept=None, slope=None, elements=None, inverse=True, sum_elements=True):
        """
        Initializes an Affine object with given slopes and intercepts or elements.
        The slopes correspond to elements, which are differentiated from pieces.

        When sum_elements=True: elements are horizontally summed to create aggregate pieces.
        When sum_elements=False: elements are kept as separate pieces (for discontinuous functions).

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
        sum_elements : bool, optional
            Whether to sum elements together (True) or keep them as separate
            pieces (False). Default is True.

        Raises
        ------
        ValueError
            If the lengths of `slope` and `intercept` do not match.
        """

        super().__init__(intercept, slope, elements, inverse, sum_elements)

        # Special handling for perfectly elastic curves - they can't be summed
        # so they'll only have one element and don't need horizontal_sum
        if self.has_perfectly_elastic_segment:
            # Set up minimal structure for a single horizontal curve
            pieces = [self.elements[0]]
            self.pieces = pieces
            cuts = [0, np.inf]
            mids = [self.elements[0].intercept]
            sections = [(0, np.inf)]
            qsections = [(0, np.inf)]
        elif not self.sum_elements:
            # Non-summing mode: keep elements as separate pieces
            pieces = self.elements
            self.pieces = pieces
            # Create sections based on element domains
            sections = []
            qsections = []
            cuts = []
            for element in self.elements:
                if hasattr(element, '_domain') and element._domain:
                    domain = element._domain
                    sections.append((min(domain), max(domain)))
                    qsections.append((min(domain), max(domain)))
                    cuts.extend([min(domain), max(domain)])
            # Remove duplicates and sort cuts
            cuts = sorted(list(set(cuts))) if cuts else [0, np.inf]
            mids = [(a + b) / 2 for a, b in sections] if sections else [0]
        else:
            # Normal processing for non-horizontal curves
            pieces, cuts, mids = horizontal_sum(*self.elements)
            self.pieces = pieces
            # store piecewise info
            sections = [(cuts[i], cuts[i+1]) for i in range(len(cuts)-1)]
            qsections = [ (self.q(ps[0]), self.q(ps[1]))  for ps in sections]
            sections.append( (cuts[-1], np.inf) )
        # Skip the q() calls for perfectly elastic curves to avoid warnings
        if not self.has_perfectly_elastic_segment:
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
            intersections = [
                intersection(pieces[i], pieces[i + 1])
                for i in range(len(pieces) - 1)
                if pieces[i] and pieces[i + 1]
            ]

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
        # Filter out any None pieces
        valid_pieces = [piece for piece in self.pieces if piece]
        if not valid_pieces:
            return None

        # Check if this is the last piece
        last_piece = valid_pieces[-1]

        for piece in valid_pieces:
            q0, q1 = np.min(piece._domain), np.max(piece._domain)

            if piece is last_piece:
                # Last piece: use [a,b] (closed interval)
                if q0 <= q <= q1:
                    return piece
            else:
                # Not the last piece: use [a,b) (right-open interval)
                if q0 <= q < q1:
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

        valid_pieces = [piece for piece in self.pieces if piece]
        if valid_pieces:
            last_piece = valid_pieces[-1]

        for piece in self.pieces:
            if piece:
                a, b = piece._domain
                if piece is last_piece:
                    # Last piece: use [a,b] convention
                    if (a <= x <= b) or (a >= x >= b):
                        return piece(x)
                else:
                    # Interior piece: use [a,b) convention
                    if (a <= x < b) or (a >= x > b):
                        return piece(x)
        # might be x out of limits
        return np.nan
        #return np.sum([np.max([0, c(x)]) for c in self.elements])

    def q(self, p):
        # returns q given p
        if not self.sum_elements:
            # Non-summing mode: find the piece that contains this price
            valid_pieces = [
                piece
                for piece in self.pieces
                if piece and hasattr(piece, '_domain') and piece._domain
            ]
            if valid_pieces:
                last_piece = valid_pieces[-1]

            for piece in valid_pieces:
                domain = piece._domain
                a, b = np.min(domain), np.max(domain)

                if piece is last_piece:
                    # Last piece: use [a,b] convention
                    if a <= p <= b:
                        try:
                            q_val = piece.q(p)
                            if np.isfinite(q_val) and q_val >= 0:
                                return q_val
                        except:
                            continue
                else:
                    # Interior piece: use [a,b) convention
                    if a <= p < b:
                        try:
                            q_val = piece.q(p)
                            if np.isfinite(q_val) and q_val >= 0:
                                return q_val
                        except:
                            continue
            return 0
        else:
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
            # Use [a,b) convention: left inclusive, right exclusive
            pc = [p for p in self.pieces if p and (np.min(p._domain) <= q < np.max(p._domain))]
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
            The maximum quantity to consider for setting the x-axis limit. If
            None, it will be automatically determined.
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
            update_axes_limits(ax)

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

        if color is None:
            color = AREA_FILLS[0]  # Default color

        if ax is None:
            ax = self.plot(max_q=max_q)
        for piece in self.pieces:
            if piece:
                piece.plot_area(p,
                             q=q,
                             ax=ax,
                             color=color,
                             alpha=alpha)

        update_axes_limits(ax)

        return ax

    def surplus(self, p, q=None):
        '''
        Returns surplus area. The areas are negative for producer surplus.
        '''
        if q is None:
            q = self.q(p)

        if q > 0:

            # find inframarginal surplus
            # Find pieces completely to the left of q (using [a,b) convention)
            trapezoids = [piece for piece in self.pieces if piece and (np.max(piece._domain) <= q)]
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
