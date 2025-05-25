import unittest
from freeride.curves import Demand, Supply
from freeride.equilibrium import Equilibrium

class TestEquilibrium(unittest.TestCase):

    def setUp(self):
        # Create demand and supply curves for testing
        self.demand_curve = Demand(10, -0.5)
        self.supply_curve = Supply(2, 0.5)
        self.equilibrium = Equilibrium(self.demand_curve, self.supply_curve)

    def test_equilibrium_price(self):
        self.assertTrue(self.equilibrium.p == 6.0)

    def test_equilibrium_quantity(self):
        self.assertTrue(self.equilibrium.q == 8.0)

    def test_binding_floor(self):
        floor_price = 7
        eq_floor = Equilibrium(self.demand_curve, self.supply_curve, floor=floor_price)
        self.assertEqual(eq_floor.p, floor_price)
        self.assertEqual(eq_floor.q, self.demand_curve.q(floor_price))
        if hasattr(eq_floor, "excess_supply"):
            expected_excess = self.supply_curve.q(floor_price) - self.demand_curve.q(floor_price)
            self.assertEqual(eq_floor.excess_supply, expected_excess)

    def test_nonbinding_floor(self):
        floor_price = 5
        eq_floor = Equilibrium(self.demand_curve, self.supply_curve, floor=floor_price)
        self.assertEqual(eq_floor.p, self.equilibrium.p)
        self.assertEqual(eq_floor.q, self.equilibrium.q)
        if hasattr(eq_floor, "excess_supply"):
            self.assertEqual(eq_floor.excess_supply, 0)
