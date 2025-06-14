import unittest
import numpy as np
from freeride.curves import Demand
from freeride.costs import Cost
from freeride.monopoly import Monopoly


class TestMonopoly(unittest.TestCase):
    def test_basic_outcome(self):
        demand = Demand(10, -1)
        cost = Cost(0, 2)
        m = Monopoly(demand, cost)
        self.assertAlmostEqual(m.q, 4.0)
        self.assertAlmostEqual(m.p, 6.0)
        self.assertAlmostEqual(m.profit, 16.0)

    def test_piecewise_demand_zero_cost(self):
        """Profit maximization with piecewise demand and zero cost."""
        demand = Demand([10, 5], [-1, -1])
        cost = Cost(0, 0)
        m = Monopoly(demand, cost)
        self.assertAlmostEqual(m.q, 7.5)
        self.assertAlmostEqual(m.p, 3.75)
        self.assertAlmostEqual(m.profit, 28.125)

    def test_kinked_demand_monopoly(self):
        """Test monopoly with kinked demand curve (discontinuous MR)."""
        # Create a kinked demand: steep segment + flat segment
        d1 = Demand(20, -1)    # P = 20 - Q, steep segment
        d2 = Demand(10, -0.5)  # P = 10 - 0.5*Q, flat segment
        kinked_demand = d1 + d2
        
        # Use constant marginal cost
        cost = Cost(0, 3)  # MC = 3
        m = Monopoly(kinked_demand, cost)
        
        # Verify this is truly profit-maximizing by checking grid
        q_grid = np.linspace(0.1, 25, 1000)
        profits = []
        for q in q_grid:
            p = kinked_demand.p(q)
            if p > 0:  # Only consider positive prices
                profit = p * q - cost.cost(q)
                profits.append(profit)
            else:
                profits.append(-np.inf)
        
        max_profit_grid = max(profits)
        
        # Our solution should be within 1% of the grid maximum
        self.assertGreater(m.profit, 0.99 * max_profit_grid)

    def test_kinked_demand_with_quadratic_cost(self):
        """Test kinked demand with quadratic cost function."""
        # Create kinked demand
        d1 = Demand(15, -0.8)   # P = 15 - 0.8*Q
        d2 = Demand(8, -0.3)    # P = 8 - 0.3*Q  
        kinked_demand = d1 + d2
        
        # Quadratic cost: TC = 2 + Q + 0.1*Q^2, so MC = 1 + 0.2*Q
        cost = Cost([2, 1, 0.1])
        m = Monopoly(kinked_demand, cost)
        
        # Verify this is profit-maximizing using grid search
        q_grid = np.linspace(0.1, 30, 2000)
        profits = []
        for q in q_grid:
            p = kinked_demand.p(q)
            if p > 0:
                profit = p * q - cost.cost(q)
                profits.append(profit)
            else:
                profits.append(-np.inf)
                
        max_profit_grid = max(profits)
        best_q_idx = np.argmax(profits)
        best_q_grid = q_grid[best_q_idx]
        
        # Our solution should be very close to grid optimum
        self.assertGreater(m.profit, 0.99 * max_profit_grid)
        self.assertAlmostEqual(m.q, best_q_grid, delta=0.1)

    def test_kinked_demand_single_segment_only(self):
        """Test kinked demand where monopolist serves only one segment."""
        # Use your exact suggestion: P = 10 - Q and P = 1 - 10*Q
        d1 = Demand(10, -1)     # P = 10 - Q  
        d2 = Demand(1, -10)     # P = 1 - 10*Q (very steep, low willingness to pay)
        kinked_demand = d1 + d2
        
        # With MC = 0, monopolist will choose Q where MR = 0 on the profitable segment
        cost = Cost(0, 0)  
        m = Monopoly(kinked_demand, cost)
        
        # For first segment P = 10 - Q, MR = 10 - 2Q
        # Setting MR = 0: Q = 5, P = 5
        # At Q = 5, first segment gives profit = 5 * 5 = 25
        # Second segment at any reasonable Q gives much lower prices/profits
        # So monopolist should choose Q = 5, P = 5 (still pricing above second segment)
        
        self.assertAlmostEqual(m.q, 5.0, places=1)  
        self.assertAlmostEqual(m.p, 5.0, places=1)  
        # Verify this price is indeed above what second segment would offer
        self.assertGreater(m.p, 1.0)  # Much higher than second segment's max price
        
        # Verify optimality with grid search
        q_grid = np.linspace(0.1, 15, 1000)
        profits = []
        for q in q_grid:
            p = kinked_demand.p(q)
            if p > 0:
                profit = p * q - cost.cost(q)
                profits.append(profit)
            else:
                profits.append(-np.inf)
        
        max_profit_grid = max(profits)
        self.assertGreater(m.profit, 0.99 * max_profit_grid)

    def test_kinked_demand_both_segments(self):
        """Test kinked demand where monopolist serves both segments."""
        # Create kinked demand where both segments are attractive
        d1 = Demand(15, -0.5)   # P = 15 - 0.5*Q, gentle slope, high willingness to pay
        d2 = Demand(12, -1)     # P = 12 - Q, steeper but still reasonable
        kinked_demand = d1 + d2
        
        # Use marginal cost that makes serving both segments optimal
        cost = Cost(0, 2)  # MC = 2
        m = Monopoly(kinked_demand, cost)
        
        # Find the kink point (where the segments meet)
        # d1: P = 15 - 0.5*Q, d2: P = 12 - Q
        # They intersect when 15 - 0.5*Q = 12 - Q
        # 3 = -0.5*Q, so Q = 6, P = 12
        kink_q = 6.0
        kink_p = 12.0
        
        # Monopolist should operate beyond the kink (serve both segments)
        self.assertGreater(m.q, kink_q)  # Should serve both segments
        self.assertLess(m.p, kink_p)     # Price should be below kink point
        
        # Verify optimality with grid search
        q_grid = np.linspace(0.1, 20, 1500)
        profits = []
        for q in q_grid:
            p = kinked_demand.p(q)
            if p > 0:
                profit = p * q - cost.cost(q)
                profits.append(profit)
            else:
                profits.append(-np.inf)
        
        max_profit_grid = max(profits)
        best_q_idx = np.argmax(profits)
        best_q_grid = q_grid[best_q_idx]
        
        # Verify we found the optimum
        self.assertGreater(m.profit, 0.99 * max_profit_grid)
        self.assertAlmostEqual(m.q, best_q_grid, delta=0.1)


if __name__ == "__main__":
    unittest.main()
