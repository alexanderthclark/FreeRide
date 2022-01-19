import matplotlib.pyplt as plt
import numpy as np

from equilibrium import Equilibrium


class LongRunCompetitiveEquilibrium:
    def __init__(self, demand, total_cost):
        """Create long-run equilibrium for perfectly comepetitive market with identical firms."""
        self.total_cost = total_cost
        self.demand = demand

        self.p = self.total_cost.breakeven_price()
        self.firm_q = self.total_cost.efficient_scale()

        self.market_q = self.demand.q(self.p)
        self.n_firms = self.market_q / self.firm_q

    def plot(self, fig=None):

        # fig, ax = plt.subplots(1,2, sharey = True)
        if fig == None:
            fig = plt.gcf()

        firm_ax = fig.add_subplot(1, 2, 1)

        self.total_cost.long_run_plot(firm_ax)
        firm_ax.set_title("Firm")

        mkt_ax = fig.add_subplot(1, 2, 2, sharey=firm_ax)

        supply_curve = Supply(self.p, 0)
        market_eq = Equilibrium(self.demand, supply_curve)

        market_eq.plot(mkt_ax)
        mkt_ax.set_title("Market")

        firm_ax.set_xlabel("Firm Quantity")
        mkt_ax.set_xlabel("Market Quantity")
