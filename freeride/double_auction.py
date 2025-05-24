"""Utility classes for clearing unit demand and supply in a double auction.

The auction pairs the highest demand valuations with the lowest supply
valuations and counts a trade only when the buyer's valuation is strictly
greater than the seller's valuation. When valuations tie, the pair does not
trade, resulting in a no-trade outcome for that unit.
"""

import numpy as np
import matplotlib.pyplot as plt


class UnitAgent:
    """Base class for auction participants.

    Parameters
    ----------
    *valuations : float
        Valuation for each unit that the agent is willing to buy or sell.
    endowment : int
        Initial quantity of the good owned by the agent.

    Attributes
    ----------
    valuations : list of float
        All valuations supplied at initialization.
    valuation : float
        Convenience reference to ``valuations[0]``.
    endowment : int
        Quantity of the good initially held.
    """

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
    """Agent with unit demand.

    Parameters
    ----------
    *willingness_to_pay : float
        Valuation for each unit the agent would like to purchase.
    """

    def __init__(self, *willingness_to_pay):
        super().__init__(*willingness_to_pay, endowment=0)


class UnitSupply(UnitAgent):
    """Agent with unit supply.

    Parameters
    ----------
    *willingness_to_sell : float
        Valuation for each unit the agent is willing to sell.
    """

    def __init__(self, *willingness_to_sell):
        super().__init__(*willingness_to_sell, endowment=len(willingness_to_sell))


def _sort_key(item):
    return item[1]


class DoubleAuction:
    """Clear a set of unit demand and supply agents using a double auction.

    The algorithm sorts buyers by descending valuation and sellers by ascending
    valuation. Each pair trades if and only if the buyer's valuation is strictly
    greater than the seller's. Ties are treated as no trade.

    Parameters
    ----------
    *agents : UnitDemand or UnitSupply
        Agents participating in the auction.
    """

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

        if len(self.demand) == 0 or len(self.supply) == 0:
            raise IndexError("DoubleAuction requires at least one buyer and one seller")

        price_range, n_trades = self.clear()
        self.price_range = price_range
        self.p = price_range
        self.q = n_trades

    def clear(self):
        """Determine the clearing price interval and quantity traded.

        Returns
        -------
        tuple
            ``(price_low, price_high)`` giving the range of possible clearing
            prices.
        int
            Number of trades executed under the strict ``d > s`` rule.
        """
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
        """Compute the discrete demand schedule.

        Returns
        -------
        list of tuple
            Pairs ``(price, quantity)`` sorted from the highest valuation to the
            lowest.
        """
        valuations = [d[1] for d in self.demand]
        unique_valuations = sorted(set(valuations), reverse=True)
        schedule = [
            (p, len([v for v in valuations if v >= p]))
            for p in unique_valuations
        ]
        return schedule

    def supply_schedule(self):
        """Compute the discrete supply schedule.

        Returns
        -------
        list of tuple
            Pairs ``(price, quantity)`` sorted from the lowest valuation to the
            highest.
        """
        valuations = [s[1] for s in self.supply]
        unique_valuations = sorted(set(valuations))
        schedule = [
            (p, len([v for v in valuations if v <= p]))
            for p in unique_valuations
        ]
        return schedule

    def plot(self, ax=None):
        """Plot the discrete demand and supply schedules.

        Parameters
        ----------
        ax : matplotlib.axes.Axes, optional
            Existing axes to draw on. If ``None`` a new figure and axes are
            created.

        Returns
        -------
        matplotlib.axes.Axes
            The axes containing the step plots.
        """
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
