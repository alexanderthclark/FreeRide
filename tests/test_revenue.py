import unittest
import numpy as np
from freeride.curves import Demand
from freeride.revenue import Revenue, MarginalRevenue


class TestRevenue(unittest.TestCase):
    
    def setUp(self):
        # Create a simple linear demand: P = 10 - Q
        self.demand = Demand.from_formula("P = 10 - Q")
        self.revenue = Revenue.from_demand(self.demand)
        
        # Create a piecewise demand for more complex tests (future enhancement)
        # self.piecewise_demand = ... # Would need custom construction
        
    def test_revenue_from_simple_demand(self):
        """Test revenue calculation from simple linear demand P = 10 - Q."""
        # For P = 10 - Q, Revenue R = P*Q = (10 - Q)*Q = 10Q - Q^2
        # So at Q = 2: R = 10*2 - 2^2 = 20 - 4 = 16
        self.assertAlmostEqual(self.revenue(2), 16, places=5)
        
        # At Q = 5: R = 10*5 - 5^2 = 50 - 25 = 25
        self.assertAlmostEqual(self.revenue(5), 25, places=5)
        
        # At Q = 0: R = 0
        self.assertAlmostEqual(self.revenue(0), 0, places=5)
        
    def test_revenue_maximum(self):
        """Test that revenue is maximized where MR = 0."""
        # For P = 10 - Q, MR = 10 - 2Q
        # MR = 0 when Q = 5, and max revenue = 25
        q_max = 5
        max_revenue = 25
        
        # Check that revenue at Q = 5 is indeed the maximum
        self.assertAlmostEqual(self.revenue(q_max), max_revenue, places=5)
        
        # Check that revenue is lower at nearby points
        self.assertLess(self.revenue(q_max - 0.1), max_revenue)
        self.assertLess(self.revenue(q_max + 0.1), max_revenue)
        
    def test_revenue_properties(self):
        """Test basic properties of revenue curve."""
        # Revenue should be 0 at Q = 0 and Q = 10 (where P = 0)
        self.assertAlmostEqual(self.revenue(0), 0, places=5)
        self.assertAlmostEqual(self.revenue(10), 0, places=5)
        
        # Revenue should be positive between 0 and 10
        for q in [1, 3, 7, 9]:
            self.assertGreater(self.revenue(q), 0)


class TestMarginalRevenue(unittest.TestCase):
    
    def setUp(self):
        # Create a simple linear demand: P = 10 - Q
        self.demand = Demand.from_formula("P = 10 - Q")
        self.marginal_revenue = MarginalRevenue.from_demand(self.demand)
        
    def test_marginal_revenue_from_simple_demand(self):
        """Test marginal revenue calculation from simple linear demand P = 10 - Q."""
        # For P = 10 - Q, MR = 10 - 2Q
        # At Q = 2: MR = 10 - 2*2 = 6
        self.assertAlmostEqual(self.marginal_revenue(2), 6, places=5)
        
        # At Q = 0: MR = 10
        self.assertAlmostEqual(self.marginal_revenue(0), 10, places=5)
        
        # At Q = 5: MR = 0
        self.assertAlmostEqual(self.marginal_revenue(5), 0, places=5)
        
    def test_marginal_revenue_properties(self):
        """Test basic properties of marginal revenue curve."""
        # For linear demand, MR should have twice the slope
        # P = 10 - Q has slope -1, so MR = 10 - 2Q has slope -2
        
        # MR should decline as quantity increases
        self.assertGreater(self.marginal_revenue(1), self.marginal_revenue(2))
        self.assertGreater(self.marginal_revenue(2), self.marginal_revenue(3))
        
        # MR should be zero where revenue is maximized
        self.assertAlmostEqual(self.marginal_revenue(5), 0, places=5)
        
    def test_marginal_revenue_intercept(self):
        """Test that MR has same intercept as demand but twice the slope."""
        # For P = 10 - Q, MR should be 10 - 2Q
        # Both should have intercept of 10
        self.assertAlmostEqual(self.marginal_revenue(0), 10, places=5)
        self.assertAlmostEqual(self.demand.p(0), 10, places=5)


class TestRevenueIntegration(unittest.TestCase):
    
    def setUp(self):
        # Test with different demand curves
        self.steep_demand = Demand.from_formula("P = 20 - 4*Q")  # Steep demand
        self.flat_demand = Demand.from_formula("P = 10 - 0.5*Q")  # Flat demand
        
    def test_revenue_from_steep_demand(self):
        """Test revenue calculation with steep demand curve."""
        revenue = Revenue.from_demand(self.steep_demand)
        # P = 20 - 4Q, so R = (20 - 4Q)*Q = 20Q - 4Q^2
        # At Q = 1: R = 20 - 4 = 16
        self.assertAlmostEqual(revenue(1), 16, places=5)
        
    def test_revenue_from_flat_demand(self):
        """Test revenue calculation with flat demand curve."""
        revenue = Revenue.from_demand(self.flat_demand)
        # P = 10 - 0.5Q, so R = (10 - 0.5Q)*Q = 10Q - 0.5Q^2
        # At Q = 2: R = 20 - 2 = 18
        self.assertAlmostEqual(revenue(2), 18, places=5)
        
    def test_marginal_revenue_slopes(self):
        """Test that MR has twice the slope of demand."""
        steep_mr = MarginalRevenue.from_demand(self.steep_demand)
        flat_mr = MarginalRevenue.from_demand(self.flat_demand)
        
        # Steep demand: P = 20 - 4Q, MR = 20 - 8Q
        self.assertAlmostEqual(steep_mr(0), 20, places=5)
        self.assertAlmostEqual(steep_mr(1), 12, places=5)  # 20 - 8*1
        
        # Flat demand: P = 10 - 0.5Q, MR = 10 - Q
        self.assertAlmostEqual(flat_mr(0), 10, places=5)
        self.assertAlmostEqual(flat_mr(2), 8, places=5)   # 10 - 1*2


if __name__ == '__main__':
    unittest.main()