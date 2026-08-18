"""Test horizontal (perfectly elastic) curve handling"""
import unittest
import warnings
import numpy as np
from freeride.curves import Supply, Demand
from freeride.equilibrium import Equilibrium


class TestHorizontalCurves(unittest.TestCase):
    """Test cases for horizontal (perfectly elastic) curves."""

    def test_horizontal_supply_creation_warns(self):
        """Test that creating horizontal supply triggers a warning."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            # Filter out numpy warnings
            warnings.filterwarnings("ignore", category=DeprecationWarning)
            warnings.filterwarnings("ignore", message="The truth value")

            s = Supply(5, 0)

            # Should have at least one warning about perfectly elastic curve
            elastic_warnings = [warning for warning in w
                              if warning.category == UserWarning and
                              "perfectly elastic supply" in str(warning.message)]
            self.assertGreater(len(elastic_warnings), 0)

    def test_horizontal_demand_creation_warns(self):
        """Test that creating horizontal demand triggers a warning."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            # Filter out numpy warnings
            warnings.filterwarnings("ignore", category=DeprecationWarning)
            warnings.filterwarnings("ignore", message="The truth value")

            d = Demand(10, 0)

            # Should have at least one warning about perfectly elastic curve
            elastic_warnings = [warning for warning in w
                              if warning.category == UserWarning and
                              "perfectly elastic demand" in str(warning.message)]
            self.assertGreater(len(elastic_warnings), 0)

    def test_horizontal_supply_q_method(self):
        """Test the q method for horizontal supply curves."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            s = Supply(5, 0)  # Horizontal at P=5

            # At P=5, should return inf (with warning in real use)
            self.assertTrue(np.isinf(s.q(5)))

            # Above P=5, should return inf
            self.assertTrue(np.isinf(s.q(6)))

            # Below P=5, should return 0
            self.assertEqual(s.q(4), 0)

    def test_horizontal_demand_q_method(self):
        """Test the q method for horizontal demand curves."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            d = Demand(10, 0)  # Horizontal at P=10

            # At P=10, should return inf (with warning in real use)
            self.assertTrue(np.isinf(d.q(10)))

            # Above P=10, should return 0
            self.assertEqual(d.q(11), 0)

            # Below P=10, should return inf
            self.assertTrue(np.isinf(d.q(9)))

    def test_equilibrium_allows_horizontal_supply_with_regular_demand(self):
        """Horizontal supply with regular demand should produce a unique point."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            s = Supply(5, 0)  # Horizontal supply
            d = Demand(10, -1)  # Normal demand

            eq = Equilibrium(d, s)
            self.assertEqual(eq.p, 5)
            self.assertEqual(eq.q, 5)

    def test_equilibrium_allows_horizontal_demand_with_regular_supply(self):
        """Horizontal demand with regular supply should produce a unique point."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            d = Demand(8, 0)  # Horizontal demand
            s = Supply(2, 1)  # Normal supply

            eq = Equilibrium(d, s)
            self.assertEqual(eq.p, 8)
            self.assertEqual(eq.q, 6)

    def test_equilibrium_horizontal_horizontal_is_indeterminate(self):
        """Equal fixed-price demand and supply should raise an indeterminate error."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            d = Demand(8, 0)
            s = Supply(8, 0)

            with self.assertRaises(ValueError) as cm:
                Equilibrium(d, s)

            self.assertIn(
                "economically indeterminate quantity at fixed price",
                str(cm.exception),
            )
