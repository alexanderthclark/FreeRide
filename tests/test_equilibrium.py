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

    def test_free_market_has_no_market_gap(self):
        self.assertAlmostEqual(self.equilibrium.quantity_demanded, 8.0)
        self.assertAlmostEqual(self.equilibrium.quantity_supplied, 8.0)
        self.assertAlmostEqual(self.equilibrium.shortage, 0.0)
        self.assertAlmostEqual(self.equilibrium.surplus, 0.0)

    def test_binding_ceiling_gap_properties(self):
        ceiling_price = 5
        eq_ceiling = Equilibrium(
            self.demand_curve,
            self.supply_curve,
            ceiling=ceiling_price,
        )
        self.assertEqual(eq_ceiling.p, ceiling_price)
        self.assertAlmostEqual(eq_ceiling.q, 6.0)
        self.assertAlmostEqual(eq_ceiling.quantity_demanded, 10.0)
        self.assertAlmostEqual(eq_ceiling.quantity_supplied, 6.0)
        self.assertAlmostEqual(eq_ceiling.shortage, 4.0)
        self.assertAlmostEqual(eq_ceiling.surplus, 0.0)
        self.assertAlmostEqual(eq_ceiling.excess_demand_quantity, 4.0)

    def test_binding_floor(self):
        floor_price = 7
        eq_floor = Equilibrium(self.demand_curve, self.supply_curve, floor=floor_price)
        self.assertEqual(eq_floor.p, floor_price)
        self.assertEqual(eq_floor.q, self.demand_curve.q(floor_price))
        self.assertAlmostEqual(eq_floor.quantity_demanded, 6.0)
        self.assertAlmostEqual(eq_floor.quantity_supplied, 10.0)
        self.assertAlmostEqual(eq_floor.shortage, 0.0)
        self.assertAlmostEqual(eq_floor.surplus, 4.0)
        self.assertAlmostEqual(eq_floor.excess_supply, 4.0)

    def test_nonbinding_floor(self):
        floor_price = 5
        eq_floor = Equilibrium(self.demand_curve, self.supply_curve, floor=floor_price)
        self.assertEqual(eq_floor.p, self.equilibrium.p)
        self.assertEqual(eq_floor.q, self.equilibrium.q)
        self.assertAlmostEqual(eq_floor.shortage, 0.0)
        self.assertAlmostEqual(eq_floor.surplus, 0.0)
        self.assertAlmostEqual(eq_floor.excess_supply, 0.0)

    def test_nonbinding_ceiling_has_no_market_gap(self):
        ceiling_price = 7
        eq_ceiling = Equilibrium(
            self.demand_curve,
            self.supply_curve,
            ceiling=ceiling_price,
        )
        self.assertEqual(eq_ceiling.p, self.equilibrium.p)
        self.assertEqual(eq_ceiling.q, self.equilibrium.q)
        self.assertAlmostEqual(eq_ceiling.shortage, 0.0)
        self.assertAlmostEqual(eq_ceiling.surplus, 0.0)
