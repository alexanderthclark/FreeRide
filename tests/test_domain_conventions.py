"""Tests for domain conventions in piecewise functions."""

import unittest
import numpy as np
from freeride.curves import Demand
from freeride.revenue import MarginalRevenue
from freeride.affine import AffineElement


class TestDomainConventions(unittest.TestCase):

    def test_single_piece_closed_interval(self):
        """Single-piece functions should use [a,b] (closed interval)."""
        demand = Demand(10, -1)  # P = 10 - Q

        self.assertAlmostEqual(demand.p(0), 10.0)
        self.assertAlmostEqual(demand.p(10), 0.0)
        self.assertFalse(np.isnan(demand.p(10)))

    def test_piecewise_boundary_evaluation(self):
        """Test evaluation at segment boundaries."""
        d1 = Demand(20, -1)    # P = 20 - Q
        d2 = Demand(15, -0.5)  # P = 15 - 0.5Q
        piecewise = d1 + d2

        # Test continuity across the domain
        q_values = [0, 5, 10, 20, 30, 40, 50]
        for i in range(len(q_values) - 1):
            q1, q2 = q_values[i], q_values[i+1]
            p1, p2 = piecewise.p(q1), piecewise.p(q2)
            # Prices should decrease as quantity increases
            self.assertGreaterEqual(p1, p2)

    def test_piecewise_full_domain(self):
        """Test that piecewise functions work across full domain."""
        d1 = Demand(20, -1)    # q-intercept at 20
        d2 = Demand(15, -0.5)  # q-intercept at 30
        piecewise = d1 + d2

        # Total q-intercept is 50
        test_points = [0, 5, 10, 20, 30, 40, 49.9, 50]

        for q in test_points:
            p = piecewise.p(q)
            self.assertFalse(np.isnan(p), f"Got NaN at q={q}")

        # Right endpoint should work
        self.assertAlmostEqual(piecewise.p(50), 0.0)

    def test_active_piece_selection(self):
        """Test that correct piece is selected at boundaries."""
        d1 = Demand(20, -1)
        d2 = Demand(15, -0.5)
        piecewise = d1 + d2

        # Test that we get valid pieces at various points
        test_qs = [0, 1, 5, 10, 25, 45, 49]
        for q in test_qs:
            active = piecewise._get_active_piece(q)
            self.assertIsNotNone(active, f"No active piece at q={q}")

    def test_marginal_revenue_boundaries(self):
        """Test MarginalRevenue at piece boundaries."""
        d1 = Demand(20, -1)
        d2 = Demand(10, -0.5)
        kinked = d1 + d2
        mr = MarginalRevenue.from_demand(kinked)

        # MR should be defined across the domain
        test_qs = [0, 5, 10, 15, 20]
        for q in test_qs:
            mr_val = mr(q)
            # Should get a value (not NaN) within reasonable domain
            if q <= 20:
                self.assertFalse(np.isnan(mr_val), f"MR is NaN at q={q}")

    def test_affine_element_domain(self):
        """Test base AffineElement domain handling."""
        elem = AffineElement(10, -1)
        elem._domain = [0, 10]

        self.assertTrue(elem.in_domain(0))
        self.assertTrue(elem.in_domain(10))
        self.assertFalse(elem.in_domain(11))


if __name__ == "__main__":
    unittest.main()