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
