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

    def test_free_market_diagnostics(self):
        self.assertEqual(self.equilibrium.quantity_demanded, self.equilibrium.q)
        self.assertEqual(self.equilibrium.quantity_supplied, self.equilibrium.q)
        self.assertEqual(self.equilibrium.excess_demand(self.equilibrium.p), 0)
        self.assertEqual(self.equilibrium.shortage, 0)
        self.assertEqual(self.equilibrium.surplus_quantity, 0)

    def test_binding_ceiling_diagnostics(self):
        market = Equilibrium(self.demand_curve, self.supply_curve, ceiling=5)
        self.assertEqual(market.quantity_demanded, 10)
        self.assertEqual(market.quantity_supplied, 6)
        self.assertEqual(market.q, market.quantity_supplied)
        self.assertEqual(
            market.shortage,
            market.quantity_demanded - market.q,
        )
        self.assertEqual(market.excess_demand(market.p), 4)
        self.assertEqual(market.surplus_quantity, 0)

    def test_binding_floor_diagnostics(self):
        market = Equilibrium(self.demand_curve, self.supply_curve, floor=7)
        self.assertEqual(market.quantity_demanded, 6)
        self.assertEqual(market.quantity_supplied, 10)
        self.assertEqual(market.q, market.quantity_demanded)
        self.assertEqual(market.shortage, 0)
        self.assertEqual(
            market.surplus_quantity,
            market.quantity_supplied - market.q,
        )
        self.assertEqual(
            market.excess_demand(market.p),
            -4,
        )

    def test_nonbinding_floor_diagnostics(self):
        market = Equilibrium(self.demand_curve, self.supply_curve, floor=5)
        self.assertEqual(market.p, self.equilibrium.p)
        self.assertEqual(market.q, self.equilibrium.q)
        self.assertEqual(market.quantity_demanded, market.q)
        self.assertEqual(market.quantity_supplied, market.q)
        self.assertEqual(market.shortage, 0)
        self.assertEqual(market.surplus_quantity, 0)

    def test_nonbinding_ceiling_diagnostics(self):
        market = Equilibrium(self.demand_curve, self.supply_curve, ceiling=8)
        self.assertEqual(market.p, self.equilibrium.p)
        self.assertEqual(market.q, self.equilibrium.q)
        self.assertEqual(market.quantity_demanded, market.q)
        self.assertEqual(market.quantity_supplied, market.q)
        self.assertEqual(market.shortage, 0)
        self.assertEqual(market.surplus_quantity, 0)

    def test_nonbinding_ceiling_ignores_floating_point_residual(self):
        demand = (
            Demand.from_formula("Q = 10 - 1*P")
            + Demand.from_formula("P = 15 - 2*Q")
        )
        supply = (
            Supply.from_formula("Q = 2*P")
            + Supply.from_formula("Q = 2*P - 1")
        )
        market = Equilibrium(demand, supply, ceiling=4)
        raw_gap = market.quantity_demanded - market.quantity_supplied

        self.assertGreater(market.ceiling, market.p)
        self.assertAlmostEqual(raw_gap, 0, places=12)
        self.assertEqual(market.shortage, 0)
        self.assertEqual(market.surplus_quantity, 0)

    def test_binding_state_updates_when_ceiling_changes(self):
        market = Equilibrium(self.demand_curve, self.supply_curve, ceiling=5)
        self.assertEqual(market.shortage, 4)

        market.ceiling = 8

        self.assertEqual(market.shortage, 0)
        self.assertEqual(market.surplus_quantity, 0)

    def test_control_at_equilibrium_has_no_imbalance(self):
        ceiling = Equilibrium(self.demand_curve, self.supply_curve, ceiling=6)
        floor = Equilibrium(self.demand_curve, self.supply_curve, floor=6)
        self.assertEqual(ceiling.shortage, 0)
        self.assertEqual(floor.surplus_quantity, 0)

    def test_tax_uses_consumer_and_producer_prices(self):
        market = Equilibrium(
            self.demand_curve,
            self.supply_curve,
            tax=2,
        )
        self.assertNotEqual(market.p_consumer, market.p_producer)
        self.assertEqual(market.quantity_demanded, market.q)
        self.assertEqual(market.quantity_supplied, market.q)
        self.assertEqual(market.shortage, 0)
        self.assertEqual(market.surplus_quantity, 0)

    def test_imports_are_not_a_shortage(self):
        market = Equilibrium(
            self.demand_curve,
            self.supply_curve,
            world_price=5,
        )
        self.assertEqual(
            market.imports,
            market.quantity_demanded - market.quantity_supplied,
        )
        self.assertEqual(market.excess_demand(market.p), market.imports)
        self.assertEqual(market.shortage, 0)
        self.assertEqual(market.surplus_quantity, 0)

    def test_exports_are_not_a_price_floor_surplus(self):
        market = Equilibrium(
            self.demand_curve,
            self.supply_curve,
            world_price=8,
        )
        self.assertEqual(
            market.exports,
            market.quantity_supplied - market.quantity_demanded,
        )
        self.assertEqual(market.excess_demand(market.p), -market.exports)
        self.assertEqual(market.shortage, 0)
        self.assertEqual(market.surplus_quantity, 0)
