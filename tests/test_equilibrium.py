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

    def test_binding_ceiling_reports_shortage(self):
        market = Equilibrium(self.demand_curve, self.supply_curve, ceiling=5)
        self.assertEqual(market.quantity_demanded, 10)
        self.assertEqual(market.quantity_supplied, 6)
        self.assertEqual(market.shortage, 4)
        self.assertEqual(market.excess_supply, 0)

    def test_binding_floor_reports_excess_supply(self):
        market = Equilibrium(self.demand_curve, self.supply_curve, floor=7)
        self.assertEqual(market.quantity_demanded, 6)
        self.assertEqual(market.quantity_supplied, 10)
        self.assertEqual(market.shortage, 0)
        self.assertEqual(market.excess_supply, 4)

    def test_nonbinding_price_control_has_no_shortage(self):
        market = Equilibrium(self.demand_curve, self.supply_curve, ceiling=8)
        self.assertEqual(market.shortage, 0)

    def test_control_at_equilibrium_has_no_imbalance(self):
        ceiling = Equilibrium(self.demand_curve, self.supply_curve, ceiling=6)
        floor = Equilibrium(self.demand_curve, self.supply_curve, floor=6)
        self.assertEqual(ceiling.shortage, 0)
        self.assertEqual(floor.excess_supply, 0)

    def test_trade_imbalance_is_not_a_shortage(self):
        market = Equilibrium(
            self.demand_curve,
            self.supply_curve,
            world_price=5,
        )
        self.assertGreater(market.imports, 0)
        self.assertEqual(market.shortage, 0)
        self.assertEqual(market.excess_supply, 0)
