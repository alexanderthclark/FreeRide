import unittest
import numpy as np
from freeride.curves import Demand, Supply, PPF


class TestReprMethods(unittest.TestCase):
    """Test __repr__ methods for Demand, Supply, and PPF classes."""
    
    def test_demand_repr_simple(self):
        """Test basic demand curve representations."""
        # Standard demand: P = 10 - Q
        d1 = Demand(10, -1)
        self.assertEqual(repr(d1), "Demand: P = 10-Q")
        
        # Demand with different slope: P = 20 - 2Q
        d2 = Demand(20, -2)
        self.assertEqual(repr(d2), "Demand: P = 20-2Q")
        
        # Demand with fractional slope: P = 15 - 0.5Q
        d3 = Demand(15, -0.5)
        self.assertEqual(repr(d3), "Demand: P = 15-0.5Q")
        
        # Demand with small intercept: P = 0.5 - Q
        d4 = Demand(0.5, -1)
        self.assertEqual(repr(d4), "Demand: P = 0.5-Q")
        
    def test_demand_repr_special_cases(self):
        """Test special cases for demand representations."""
        # Perfectly elastic demand (horizontal)
        d1 = Demand(5, 0)
        self.assertEqual(repr(d1), "Demand: P = 5")
        
        # Piecewise demand
        d_piece1 = Demand(20, -1)
        d_piece2 = Demand(10, -0.5)
        d_piecewise = d_piece1 + d_piece2
        self.assertEqual(repr(d_piecewise), "Demand: 2-piece piecewise function")
        
    def test_supply_repr_simple(self):
        """Test basic supply curve representations."""
        # Standard supply: P = 2 + Q
        s1 = Supply(2, 1)
        self.assertEqual(repr(s1), "Supply: P = 2+Q")
        
        # Supply with different slope: P = 5 + 2Q
        s2 = Supply(5, 2)
        self.assertEqual(repr(s2), "Supply: P = 5+2Q")
        
        # Supply with fractional slope: P = 1 + 0.5Q
        s3 = Supply(1, 0.5)
        self.assertEqual(repr(s3), "Supply: P = 1+0.5Q")
        
        # Supply through origin: P = Q
        s4 = Supply(0, 1)
        self.assertEqual(repr(s4), "Supply: P = Q")
        
        # Supply with negative intercept: P = -2 + 3Q
        s5 = Supply(-2, 3)
        self.assertEqual(repr(s5), "Supply: P = -2+3Q")
        
    def test_supply_repr_special_cases(self):
        """Test special cases for supply representations."""
        # Perfectly elastic supply (horizontal)
        s1 = Supply(3, 0)
        self.assertEqual(repr(s1), "Supply: P = 3")
        
        # Piecewise supply
        s_piece1 = Supply(0, 1)
        s_piece2 = Supply(10, 2)
        s_piecewise = s_piece1 + s_piece2
        self.assertEqual(repr(s_piecewise), "Supply: 2-piece piecewise function")
        
    def test_ppf_repr_simple(self):
        """Test basic PPF representations."""
        # Standard PPF: y = 10 - x
        ppf1 = PPF(10, -1)
        self.assertEqual(repr(ppf1), "PPF: y = 10-x")
        
        # PPF with different slope: y = 20 - 2x
        ppf2 = PPF(20, -2)
        self.assertEqual(repr(ppf2), "PPF: y = 20-2x")
        
        # PPF through origin: y = -x
        ppf3 = PPF(0, -1)
        self.assertEqual(repr(ppf3), "PPF: y = -x")
        
        # PPF with fractional slope: y = 15 - 0.5x
        ppf4 = PPF(15, -0.5)
        self.assertEqual(repr(ppf4), "PPF: y = 15-0.5x")
        
    def test_ppf_repr_piecewise(self):
        """Test piecewise PPF representation."""
        # Create two PPF segments
        ppf1 = PPF(10, -2)
        ppf2 = PPF(20, -1)
        ppf_combined = ppf1 + ppf2
        self.assertEqual(repr(ppf_combined), "PPF: 2-piece frontier")
        
    def test_number_formatting(self):
        """Test that numbers are formatted cleanly without unnecessary decimals."""
        # Integer values should not show .0
        d1 = Demand(10.0, -1.0)
        self.assertEqual(repr(d1), "Demand: P = 10-Q")
        
        s1 = Supply(5.0, 2.0)
        self.assertEqual(repr(s1), "Supply: P = 5+2Q")
        
        # But fractional values should be preserved
        d2 = Demand(10.5, -1.5)
        self.assertEqual(repr(d2), "Demand: P = 10.5-1.5Q")
        
        s2 = Supply(2.5, 0.75)
        self.assertEqual(repr(s2), "Supply: P = 2.5+0.75Q")
        
    def test_sign_handling(self):
        """Test that signs are handled correctly in all cases."""
        # Very small numbers should use g formatting
        d1 = Demand(10, -0.0001)
        self.assertEqual(repr(d1), "Demand: P = 10-0.0001Q")
        
        # Very large numbers
        s1 = Supply(1000000, 1000)
        self.assertEqual(repr(s1), "Supply: P = 1e+06+1000Q")


if __name__ == '__main__':
    unittest.main()