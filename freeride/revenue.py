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
    
    def __repr__(self):
        """Text representation for terminal/console."""
        if len(self.elements) == 1:
            elem = self.elements[0]
            # Format revenue function R(q) = aq + bq^2
            terms = []
            if elem.coef[1] != 0:  # Linear term
                if elem.coef[1] == 1:
                    terms.append("q")
                elif elem.coef[1] == -1:
                    terms.append("-q")
                else:
                    terms.append(f"{elem.coef[1]:g}q")
            if elem.coef[2] != 0:  # Quadratic term
                if elem.coef[2] == 1:
                    terms.append("q^2")
                elif elem.coef[2] == -1:
                    terms.append("-q^2")
                else:
                    terms.append(f"{elem.coef[2]:g}q^2")
            
            if not terms:
                revenue_str = "0"
            else:
                revenue_str = terms[0]
                for term in terms[1:]:
                    if term.startswith("-"):
                        revenue_str += f" {term}"
                    else:
                        revenue_str += f" + {term}"
            
            return f"Revenue: R(q) = {revenue_str}"
        else:
            return f"Revenue: {len(self.elements)}-piece piecewise quadratic"


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
    
    def __repr__(self):
        """Text representation for terminal/console."""
        if len(self.elements) == 1:
            elem = self.elements[0]
            # Format using :+g to handle signs automatically
            if elem.slope == 0:
                return f"MarginalRevenue: MR(q) = {elem.intercept:g}"
            elif elem.slope == 1:
                slope_part = "+q"
            elif elem.slope == -1:
                slope_part = "-q"
            else:
                slope_part = f"{elem.slope:+g}q"
            
            if elem.intercept == 0:
                # Remove leading + for cleaner display when no intercept
                return f"MarginalRevenue: MR(q) = {slope_part.lstrip('+')}"
            else:
                return f"MarginalRevenue: MR(q) = {elem.intercept:g}{slope_part}"
        else:
            return f"MarginalRevenue: {len(self.elements)}-piece piecewise linear"
