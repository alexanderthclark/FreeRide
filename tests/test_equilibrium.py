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

    def test_symmetric_tax_incidence(self):
        demand = Demand(10, -1)
        supply = Supply(0, 1)
        eq_tax = Equilibrium(demand, supply, tax=2)
        self.assertAlmostEqual(eq_tax.tax_wedge, 2.0)
        self.assertAlmostEqual(eq_tax.consumer_tax_burden, 1.0)
        self.assertAlmostEqual(eq_tax.producer_tax_burden, 1.0)
        self.assertAlmostEqual(eq_tax.consumer_tax_share, 0.5)
        self.assertAlmostEqual(eq_tax.producer_tax_share, 0.5)

    def test_inelastic_demand_places_more_tax_burden_on_consumers(self):
        demand = Demand(10, -4)
        supply = Supply(0, 1)
        eq_tax = Equilibrium(demand, supply, tax=2)
        self.assertAlmostEqual(eq_tax.consumer_tax_burden, 1.6)
        self.assertAlmostEqual(eq_tax.producer_tax_burden, 0.4)
        self.assertGreater(
            eq_tax.consumer_tax_share,
            eq_tax.producer_tax_share,
        )
        self.assertAlmostEqual(
            eq_tax.consumer_tax_share + eq_tax.producer_tax_share,
            1.0,
        )

    def test_no_tax_has_zero_tax_incidence(self):
        self.assertAlmostEqual(self.equilibrium.tax_wedge, 0.0)
        self.assertAlmostEqual(self.equilibrium.consumer_tax_burden, 0.0)
        self.assertAlmostEqual(self.equilibrium.producer_tax_burden, 0.0)
        self.assertAlmostEqual(self.equilibrium.consumer_tax_share, 0.0)
        self.assertAlmostEqual(self.equilibrium.producer_tax_share, 0.0)

    def test_subsidy_incidence_uses_signed_burdens(self):
        demand = Demand(10, -1)
        supply = Supply(0, 1)
        eq_subsidy = Equilibrium(demand, supply)
        eq_subsidy.subsidy = 2
        self.assertAlmostEqual(eq_subsidy.tax_wedge, -2.0)
        self.assertAlmostEqual(eq_subsidy.consumer_tax_burden, -1.0)
        self.assertAlmostEqual(eq_subsidy.producer_tax_burden, -1.0)
        self.assertAlmostEqual(eq_subsidy.consumer_tax_share, 0.5)
        self.assertAlmostEqual(eq_subsidy.producer_tax_share, 0.5)
