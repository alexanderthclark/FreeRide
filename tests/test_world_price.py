import unittest
from freeride.curves import Demand, Supply
from freeride.equilibrium import Equilibrium


class TestWorldPrice(unittest.TestCase):
    def setUp(self):
        self.demand = Demand(10, -0.5)
        self.supply = Supply(2, 0.5)

    def test_importer_at_low_world_price(self):
        eq = Equilibrium(self.demand, self.supply, world_price=4)
        self.assertAlmostEqual(eq.p, 4.0)
        self.assertAlmostEqual(eq.imports, 8.0)
        self.assertAlmostEqual(eq.exports, 0.0)

    def test_exporter_at_high_world_price(self):
        eq = Equilibrium(self.demand, self.supply, world_price=8)
        self.assertAlmostEqual(eq.p, 8.0)
        self.assertAlmostEqual(eq.exports, 8.0)
        self.assertAlmostEqual(eq.imports, 0.0)

    def test_tariff_raises_domestic_price(self):
        eq = Equilibrium(self.demand, self.supply, world_price=4, tariff=1)
        self.assertAlmostEqual(eq.p, 5.0)
        self.assertAlmostEqual(eq.imports, 4.0)
        self.assertAlmostEqual(eq.govt_revenue, 4.0)

    def test_tariff_requires_world_price(self):
        with self.assertRaises(ValueError):
            Equilibrium(self.demand, self.supply, tariff=1)
