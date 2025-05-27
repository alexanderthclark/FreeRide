import unittest
from freeride import Demand, Supply, Market


class TestIntersectionOperator(unittest.TestCase):
    """Test the & operator for creating Market objects from Demand and Supply."""
    
    def setUp(self):
        """Set up test curves."""
        self.demand = Demand(10, -1)
        self.supply = Supply(2, 1)
    
    def test_demand_and_supply(self):
        """Test Demand & Supply creates correct Market."""
        market = self.demand & self.supply
        self.assertIsInstance(market, Market)
        self.assertEqual(market.p, 6.0)
        self.assertEqual(market.q, 4.0)
    
    def test_supply_and_demand(self):
        """Test Supply & Demand creates correct Market."""
        market = self.supply & self.demand
        self.assertIsInstance(market, Market)
        self.assertEqual(market.p, 6.0)
        self.assertEqual(market.q, 4.0)
    
    def test_order_independence(self):
        """Test that order doesn't matter: d & s == s & d."""
        market1 = self.demand & self.supply
        market2 = self.supply & self.demand
        
        self.assertEqual(market1.p, market2.p)
        self.assertEqual(market1.q, market2.q)
        self.assertEqual(market1.consumer_surplus, market2.consumer_surplus)
        self.assertEqual(market1.producer_surplus, market2.producer_surplus)
    
    def test_equivalence_to_constructor(self):
        """Test that & operator gives same result as Market constructor."""
        market_intersection = self.demand & self.supply
        market_constructor = Market(self.demand, self.supply)
        
        self.assertEqual(market_intersection.p, market_constructor.p)
        self.assertEqual(market_intersection.q, market_constructor.q)
    
    def test_invalid_intersection(self):
        """Test that & operator with non-curve objects raises TypeError."""
        with self.assertRaises(TypeError):
            self.demand & "not a supply curve"
        
        with self.assertRaises(TypeError):
            self.supply & 42
    
    def test_with_formula_curves(self):
        """Test & operator with curves created from formulas."""
        d = Demand.from_formula("P = 20 - 2*Q")
        s = Supply.from_formula("P = 5 + Q")
        
        market = d & s
        self.assertIsInstance(market, Market)
        self.assertAlmostEqual(market.p, 10.0, places=2)
        self.assertAlmostEqual(market.q, 5.0, places=2)


if __name__ == '__main__':
    unittest.main()