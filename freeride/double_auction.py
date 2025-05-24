"""Utility classes for unit demand and supply in double auctions."""

import numpy as np
import matplotlib.pyplot as plt


class UnitAgent:
    """Base class storing a valuation and an endowment."""

    def __init__(self, valuation, endowment):
        self.valuation = valuation
        self.endowment = endowment

        if self.valuation < 0:
            raise ValueError("No bads. Valuations must be non-negative.")


class UnitDemand(UnitAgent):
    """Unit demand agent."""

    def __init__(self, willingness_to_pay):
        super().__init__(willingness_to_pay, 0)


class UnitSupply(UnitAgent):
    """Unit supply agent."""

    def __init__(self, willingness_to_sell):
        super().__init__(willingness_to_sell, 1)


def _sort_key(item):
    return item[1]


class DoubleAuction:
    """Simple double auction clearing unit agents."""

    def __init__(self, *agents):
        self.agents = agents

        demands = sorted(
            [(a, a.valuation) for a in agents if isinstance(a, UnitDemand)],
            key=_sort_key,
            reverse=True,
        )
        self.demand = demands

        supplies = sorted(
            [(a, a.valuation) for a in agents if isinstance(a, UnitSupply)],
            key=_sort_key,
            reverse=False,
        )
        self.supply = supplies

        price_range, n_trades = self.clear()
        self.price_range = price_range
        self.p = price_range
        self.q = n_trades

    def clear(self):
        """Determine clearing price range and number of trades."""
        total_q = sum(a.endowment for a in self.agents)
        self.valuations = sorted(
            (a.valuation for a in self.agents),
            reverse=True,
        )

        zipped = zip(self.demand, self.supply)
        n_trades = len([(d, s) for (d, s) in zipped if d[1] > s[1]])

        highest_valuations = self.valuations[:total_q]
        lowest_valuations = self.valuations[total_q:]

        price_range = lowest_valuations[0], highest_valuations[-1]
        return price_range, n_trades

    def __repr__(self):
        return f"Price range: {self.price_range}\nQuantity: {self.q}"

    def demand_schedule(self):
        """List of ``(price, quantity)`` sorted from high to low valuation."""
        valuations = [d[1] for d in self.demand]
        unique_valuations = sorted({d[1] for d in self.demand}, reverse=True)
        schedule = [
            (p, len(valuations) - idx)
            for idx, p in enumerate(valuations)
        ]
        schedule = [
            (p, len([v for v in valuations if v >= p]))
            for p in unique_valuations
        ]
        return schedule

    def supply_schedule(self):
        """List of ``(price, quantity)`` sorted from low to high valuation."""
        valuations = [s[1] for s in self.supply]
        unique_valuations = sorted({s[1] for s in self.supply})
        schedule = [
            (p, len(valuations) - idx)
            for idx, p in enumerate(valuations)
        ]
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
