"""Revenue curve utilities."""

from __future__ import annotations

from .quadratic import QuadraticElement, BaseQuadratic
from .affine import AffineElement, Affine


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
            revenue_element._domain = sorted(piece._domain)  # pylint: disable=protected-access
            elements.append(revenue_element)
        return cls(elements=elements)


class MarginalRevenue(Affine):
    """Piecewise linear marginal revenue curve.

    This class represents marginal revenue as a function of quantity.
    These curves will not necessarily be continuous for piecewise Demand.
    Uses Affine with sum_elements=False to keep pieces separate for discontinuities.
    """

    @classmethod
    def from_demand(cls, demand) -> "MarginalRevenue":
        """Construct a MarginalRevenue curve from a :class:`Demand` instance."""
        elements = []
        pieces = [p for p in demand.pieces if p]
        for piece in pieces:
            # For linear demand P = a + bQ, MR = a + 2bQ
            mr_intercept = piece.intercept
            mr_slope = 2 * piece.slope  # Slope becomes twice as steep
            mr_element = AffineElement(mr_intercept, mr_slope)
            mr_element._domain = piece._domain  # pylint: disable=protected-access  # Use same domain as demand piece
            elements.append(mr_element)

        # Create Affine object with sum_elements=False to keep pieces separate
        return cls(elements=elements, sum_elements=False)
