import matplotlib.pyplt as plt
import numpy as np


class Equilibrium:
    def __init__(self, demand, supply):
        """Equilibrium produced by demand and supply. Initialized as market equilibrium."""
        p, q = demand.equilibrium(supply)
        self.p, self.market_p = p, p
        self.q, self.market_q = q, q
        self.demand = demand
        self.supply = supply
        self.tax = 0
        self.subsidy = 0
        self.p_consumer = self.p
        self.p_producer = self.p
        self.dwl = 0
        self.externalities = False

    def plot_old(self, ax=None, annotate=False, clean=True, fresh_ticks=True):
        """deprecated"""
        if ax == None:
            ax = plt.gca()
        if self.p_producer == self.p_consumer:
            self.demand.equilibrium_plot(self.supply, ax=ax, annotate=annotate)
        else:
            pass

        if clean:
            self.plot_clean(ax, fresh_ticks=fresh_ticks)

    def plot(self, ax=None, annotate=False, clean=True, fresh_ticks=True):
        """Plot the intersection of two curves."""
        if ax == None:
            fig, ax = plt.subplots()
        # else:
        #   global ax
        for curve in self.demand, self.supply:
            curve.plot(ax=ax)

        ax.set_ylabel("Price")
        ax.set_xlabel("Quantity")

        # dashed lines
        q, p = self.q, self.p  # p can be a tuple

        if type(p) != tuple:

            ax.plot([0, q], [p, p], linestyle="dashed", color="C0")
            ax.plot([q, q], [0, p], linestyle="dashed", color="C0")
            ax.plot([q], [p], marker="o")

        else:

            max_p = np.max(p)
            ax.plot([q, q], [0, max_p], linestyle="dashed", color="C0")

            for p_ in p:
                ax.plot([0, q], [p_, p_], linestyle="dashed", color="C0")

                ax.plot([q], [p_], marker="o")

        # annotation
        if annotate:
            s = " $p = {:.1f}, q = {:.1f}$".format(p, q)
            ax.text(q, p, s, ha="left")

        if clean:
            self.plot_clean(ax, fresh_ticks=fresh_ticks)

    def plot_clean(self, ax=None, fresh_ticks=True, axis_arrows=False):
        """Clean Equilibrium plot."""
        if ax == None:
            ax = plt.gca()

        # Changes spine styling and sets limits (again reset below)
        self.demand.equilibrium_plot_cleaner(self.supply, ax)

        # check previous ticks
        prev_x = set(ax.get_xticks())
        prev_y = set(ax.get_yticks())

        # label only important points on axes
        important_y = np.min(self.p), np.max(self.p), self.demand.intercept
        important_y = sorted(list(set(important_y)))  # if p not a tuple
        important_x = self.q, self.demand.q_intercept

        if self.supply.intercept >= 0:
            important_y = self.supply.intercept, *important_y
        if self.supply.q_intercept > 0:
            important_x = self.supply.q_intercept, *important_x

        combined_xticks = set(important_x).union(prev_x)
        combined_yticks = set(important_y).union(prev_y)

        if fresh_ticks:
            ax.set_xticks([x for x in important_x if not np.isnan(x)])
            ax.set_yticks([x for x in important_y if not np.isnan(x)])
        else:
            ax.set_xticks(sorted(list([x for x in combined_xticks if not np.isnan(x)])))
            ax.set_yticks(sorted(list([x for x in combined_yticks if not np.isnan(x)])))

        # label demand and supply curves
        # not written yet

        # set limits
        x_int = self.demand.q_intercept * 1.04
        if np.isnan(x_int):
            x_int = 2 * self.q

        ax.set_xlim(0, x_int)
        ax.set_ylim(0, self.demand.intercept * 1.04)

        xlims = ax.get_xlim()
        ylims = ax.get_ylim()

        if axis_arrows:
            # Add arrows to axes
            ax.plot(xlims[1], 0, ">k", clip_on=False)
            ax.plot(0, ylims[1], "^k", clip_on=False)

    def surplus(self):
        """Returns producer surplus, consumer surplus, government revenue.
        Negative government revenue indicates government expenditure."""
        ps = self.supply.producer_surplus(e.p_producer)
        cs = self.demand.consumer_surplus(e.p_consumer)
        # Govt revenue
        govt = (self.tax - self.subsidy) * self.q

        return ps, cs, govt

    def plot_surplus(self, ax=None, annotate=True, items=["cs", "ps", "govt"]):

        if ax == None:
            ax = plt.gca()

        items = [x.lower() for x in items]

        p, q = self.p, self.q

        # CS region
        if "cs" in items:
            cs_plot = ax.fill_between(
                [0, q],
                y1=[self.demand.intercept, self.p_consumer],
                y2=self.p_consumer,
                alpha=0.1,
            )

        # fix later for negative
        if "ps" in items:
            ps_plot = ax.fill_between(
                [0, q],
                y1=[self.supply.intercept, self.p_producer],
                y2=self.p_producer,
                color="C1",
                alpha=0.1,
            )

        if type(self.p) == tuple:
            if "govt" in items:
                high_price, low_price = np.max(p), np.min(p)
                g_plot = ax.fill_between(
                    [0, q], y1=high_price, y2=low_price, color="C2", alpha=0.1
                )

        if annotate:
            x_pos = self.q / 3

            # meean between price and along supply curve
            ps_y = np.mean(
                [self.p_producer, self.supply.intercept + self.supply.slope * x_pos]
            )
            cs_y = np.mean(
                [self.p_consumer, self.demand.intercept + self.demand.slope * x_pos]
            )
            govt_y = np.mean(p)

            if type(self.p) == tuple:
                if "govt" in items:
                    ax.text(self.q / 4, govt_y, "Govt", ha="center", va="center")

            if "cs" in items:
                ax.text(x_pos, cs_y, "CS", ha="center", va="center")
            if "ps" in items:
                ax.text(x_pos, ps_y, "PS", ha="center", va="center")

    def plot_dwl(self, ax=None, annotate=True):
        """Plot deadweight loss region."""
        if ax == None:
            ax = plt.gca()

        market_p, market_q = self.demand.equilibrium(self.supply)
        p1, p2 = np.min(self.p), np.max(self.p)

        if self.tax > 0:
            ax.fill_between(
                [self.q, market_q],
                y1=(p2, market_p),
                y2=(p1, market_p),
                color="red",
                alpha=0.1,
            )

            if annotate:
                ax.text(
                    (2 / 3) * self.q + (1 / 3) * market_q,
                    np.mean(self.p),
                    " DWL",
                    ha="center",
                    va="center",
                    size=8,
                )

        elif self.subsidy > 0:
            ax.fill_between(
                [market_q, self.q],
                y1=(market_p, p2),
                y2=(market_p, p1),
                color="red",
                alpha=0.1,
            )

            if annotate:
                ax.text(
                    (2 / 3) * self.q + (1 / 3) * market_q,
                    np.mean(self.p),
                    " DWL",
                    ha="center",
                    va="center",
                    size=8,
                )

    def set_tax(self, tax):
        """Impose a per-unit tax. This overwrites other taxes or subsidies instead of adding to them.
        Nominal incidence is not considered,
        so this works for taxes/subsidies imposed on either demand or supply."""

        self.tax = tax

        # Change in market quantity
        self.distortion = self.tax / (self.supply.slope - self.demand.slope)

        # update q relative to market quantity
        self.q = self.demand.equilibrium(self.supply)[1] - self.distortion

        # Update market prices
        self.p_consumer = self.demand.intercept + self.demand.slope * self.q
        self.p_producer = self.supply.intercept + self.supply.slope * self.q
        if self.p_consumer != self.p_producer:
            self.p = self.p_consumer, self.p_producer
        else:
            self.p = self.p_consumer
        # don't allow negative quantities
        if self.q < 0:
            self.q = 0

        # calculate DWL
        self.dwl = np.abs(self.distortion * self.tax * 0.5)

        # clear any subsidy
        self.subsidy = 0

    def set_subsidy(self, subsidy):
        """Impose a per-unit subsidy. This overwrites other taxes or subsidies instead of adding to them."""
        self.set_tax(-subsidy)  # implement as negative tax
        self.subsidy = subsidy
        self.distortion = -self.distortion
        self.tax = 0  # correct tax to zero
