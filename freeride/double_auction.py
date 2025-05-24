"""Utility classes for unit demand and supply in double auctions."""

import numpy as np
import matplotlib.pyplot as plt


class UnitAgent:
    """Base class storing valuations for each unit and an endowment."""

    def __init__(self, *valuations, endowment):
        if len(valuations) == 1 and isinstance(valuations[0], (list, tuple, np.ndarray)):
            valuations = valuations[0]

        if len(valuations) == 0:
            raise ValueError("At least one valuation is required")

        self.valuations = [float(v) for v in valuations]
        self.valuation = self.valuations[0]
        self.endowment = int(endowment)

        if any(v < 0 for v in self.valuations):
            raise ValueError("No bads. Valuations must be non-negative.")


class UnitDemand(UnitAgent):
    """Unit demand agent."""

    def __init__(self, *willingness_to_pay):
        super().__init__(*willingness_to_pay, endowment=0)


class UnitSupply(UnitAgent):
    """Unit supply agent."""

    def __init__(self, *willingness_to_sell):
        super().__init__(*willingness_to_sell, endowment=len(willingness_to_sell))


def _sort_key(item):
    return item[1]


class DoubleAuction:
    """Simple double auction clearing unit agents."""

    def __init__(self, *agents):
        self.agents = agents

        demands = []
        for a in agents:
            if isinstance(a, UnitDemand):
                for v in a.valuations:
                    demands.append((a, v))
        demands = sorted(demands, key=_sort_key, reverse=True)
        self.demand = demands

        supplies = []
        for a in agents:
            if isinstance(a, UnitSupply):
                for v in a.valuations:
                    supplies.append((a, v))
        supplies = sorted(supplies, key=_sort_key)
        self.supply = supplies

        price_range, n_trades = self.clear()
        self.price_range = price_range
        self.p = price_range
        self.q = n_trades

    def clear(self):
        """Determine clearing price range and number of trades."""
        total_q = sum(a.endowment for a in self.agents)
        self.valuations = sorted(
            (v for a in self.agents for v in a.valuations),
            reverse=True,
        )

        zipped = zip(self.demand, self.supply)
        n_trades = len([(d, s) for (d, s) in zipped if d[1] > s[1]])

        highest_valuations = self.valuations[:total_q]
        lowest_valuations = self.valuations[total_q:]

        price_range = (0, highest_valuations[-1]) if not lowest_valuations else (lowest_valuations[0], highest_valuations[-1])
        return price_range, n_trades

    def __repr__(self):
        return f"Price range: {self.price_range}\nQuantity: {self.q}"

    def demand_schedule(self):
        """List of ``(price, quantity)`` sorted from high to low valuation."""
        valuations = [d[1] for d in self.demand]
        unique_valuations = sorted(set(valuations), reverse=True)
        schedule = [
            (p, len([v for v in valuations if v >= p]))
            for p in unique_valuations
        ]
        return schedule

    def supply_schedule(self):
        """List of ``(price, quantity)`` sorted from low to high valuation."""
        valuations = [s[1] for s in self.supply]
        unique_valuations = sorted(set(valuations))
        schedule = [
            (p, len([v for v in valuations if v <= p]))
            for p in unique_valuations
        ]
        return schedule

    def plot(self, ax=None):
        demand = self.demand_schedule()
        demand_q = [0] + [d[1] for d in demand]
        demand_p = [np.inf] + [d[0] for d in demand]

        supply = self.supply_schedule()
        supply_p = [0] + [s[0] for s in supply]
        supply_q = [0] + [s[1] for s in supply]

        if ax is None:
            fig, ax = plt.subplots()
            ax.step(demand_q, demand_p, marker='.', color='C0')
            ax.step(supply_q, supply_p, marker='x', color='C1')

        return ax
