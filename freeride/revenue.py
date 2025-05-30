from __future__ import annotations

"""Revenue curve utilities."""

from .quadratic import QuadraticElement, BaseQuadratic


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

