"""Utilities for clearing unit demand and supply in a double auction.

The module defines light–weight agent classes representing unit demand and
unit supply as well as a :class:`DoubleAuction` class which clears a market of
these agents.  The clearing process follows the standard approach of matching
the highest demand valuations with the lowest supply valuations to determine a
range of market clearing prices and the quantity traded.
"""

import numpy as np
import matplotlib.pyplot as plt


class UnitAgent:
    """Base class for agents with unit valuations and an endowment.

    Parameters
    ----------
    *valuations : float or Sequence[float]
        Valuations for each unit held by the agent. A single iterable can be
        supplied or individual numerical arguments can be provided.
    endowment : int
        Initial quantity of the good held by the agent.

    Attributes
    ----------
    valuations : list[float]
        List of valuations for each unit.
    valuation : float
        The valuation of the first unit, provided as a convenience.
    endowment : int
        The initial quantity of the good held by the agent.
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

    def __repr__(self):
        """Return a concise representation of the agent."""
        cls_name = self.__class__.__name__
        return f"{cls_name}(endowment={self.endowment}, valuations={self.valuations})"


class UnitDemand(UnitAgent):
    """Agent demanding units of the good.

    Parameters
    ----------
    *willingness_to_pay : float or Sequence[float]
        Valuations representing the maximum prices the agent is willing to pay
        for successive units.
    """

    def __init__(self, *willingness_to_pay):
        super().__init__(*willingness_to_pay, endowment=0)


class UnitSupply(UnitAgent):
    """Agent supplying units of the good.

    Parameters
    ----------
    *willingness_to_sell : float or Sequence[float]
        Valuations representing the minimum prices the agent is willing to
        accept for successive units.
    """

    def __init__(self, *willingness_to_sell):
        super().__init__(*willingness_to_sell, endowment=len(willingness_to_sell))


def _sort_key(item):
    """Return the valuation component of ``item`` for sorting."""
    return item[1]


class DoubleAuction:
    """Clear a double auction comprised of unit agents.

    Parameters
    ----------
    *agents : UnitAgent
        Agents participating in the auction. Instances of
        :class:`UnitDemand` represent buyers and :class:`UnitSupply`
        represent sellers.

    Attributes
    ----------
    demand : list[tuple[UnitDemand, float]]
        Sorted list of demand valuations in descending order.
    supply : list[tuple[UnitSupply, float]]
        Sorted list of supply valuations in ascending order.
    p : tuple[float, float]
        Range of prices that clear the market.
    q : int
        Number of units traded at the clearing price.
    """

    def __init__(self, *agents):
        """Create a new auction with the given agents.

        Parameters
        ----------
        *agents : UnitAgent
            Agents participating in the auction.
        """
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
        """Compute the market clearing price range and trade quantity.

        Returns
        -------
        tuple
            ``(p_low, p_high)`` giving the range of prices that clear the
            market.
        int
            Number of trades executed at that price range.
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
        """Return the market demand schedule.

        Returns
        -------
        list[tuple[float, int]]
            Sequence of ``(price, quantity)`` pairs sorted from high to low
            valuation.
        """
        valuations = [d[1] for d in self.demand]
        unique_valuations = sorted(set(valuations), reverse=True)
        schedule = [
            (p, len([v for v in valuations if v >= p]))
            for p in unique_valuations
        ]
        return schedule

    def supply_schedule(self):
        """Return the market supply schedule.

        Returns
        -------
        list[tuple[float, int]]
            Sequence of ``(price, quantity)`` pairs sorted from low to high
            valuation.
        """
        valuations = [s[1] for s in self.supply]
        unique_valuations = sorted(set(valuations))
        schedule = [
            (p, len([v for v in valuations if v <= p]))
            for p in unique_valuations
        ]
        return schedule

    def plot(self, ax=None):
        """Plot the supply and demand schedules.

        Parameters
        ----------
        ax : matplotlib.axes.Axes, optional
            Axes object to draw on. A new one is created if ``None``.

        Returns
        -------
        matplotlib.axes.Axes
            Axes containing the plotted schedules.
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
