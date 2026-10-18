"""
equilibrium.py

Single-intervention partial-equilibrium model:
- Tax on consumers (closed economy)
- Price floor (closed economy)
- Price ceiling (closed economy)
- World price + tariff (small open economy)

If more than one policy is set, raise an exception.

Plotting logic:
- For a tax or price control, we compare new Q vs. autarky Q*
  and fill one red wedge for DWL.
- For a tariff, we compare new outcome vs. free-trade
  (same world_price, tariff=0)
  and fill two red wedges: under-consumption + over-production.
- Government revenue is also shaded as a rectangle:
  - For a tax => from p_producer to p_consumer, over [0..Q].
  - For a tariff => from p_world to p_world + t (if importer),
                   or p_world - t to p_world (if exporter),
                   over the range of imports/exports.
"""

import numpy as np
import matplotlib.pyplot as plt

from freeride.curves import Demand, Supply
from freeride.affine import intersection
from freeride.plotting import (
    update_axes_limits, textbook_axes, _visible_curve_pieces,
    DEMAND_COLOR, SUPPLY_COLOR, CONSUMER_FILL, PRODUCER_FILL,
    REVENUE_FILL, DWL_FILL,
)


class Equilibrium:
    """
    Equilibrium with exactly one possible intervention
    (tax/floor/ceiling/world_price+tariff).
    Raises Exception if multiple are set.

    DWL shading:
    - Tax/floor/ceiling => compare to no intervention eq => one wedge
    - Tariff => compare to free trade => two wedges
    Government revenue shading:
    - Tax => fill rectangle from p_producer to p_consumer over [0..Q]
    - Tariff => fill rectangle from p_world to p_world + t over [Q_s..Q_d]
      (if importer), or from p_world - t to p_world (if exporter).
    """

    def __init__(
            self,
            demand: Demand,
            supply: Supply,
            tax=0,
            ceiling=None,
            floor=None,
            world_price=None,
            tariff=0
    ):
        # Check for perfectly elastic or inelastic curves
        if demand.has_perfect_segment:
            raise ValueError(
                "Equilibrium does not currently support perfectly elastic or inelastic demand curves "
                "due to implementation limitations (not economic theory). "
                "These curves have indeterminate quantities at the equilibrium price."
            )
        if supply.has_perfect_segment:
            raise ValueError(
                "Equilibrium does not currently support perfectly elastic or inelastic supply curves "
                "due to implementation limitations (not economic theory). "
                "These curves have indeterminate quantities at the equilibrium price."
            )

        self.demand = demand
        self.supply = supply

        self.__tax = tax
        self.__ceiling = ceiling
        self.__floor = floor
        self.__world_price = world_price
        self.__tariff = tariff

        # Final equilibrium results
        self.q = 0
        self.p = 0
        self.__p_consumer = 0
        self.__p_producer = 0

        # For small open economy
        self._importer = None
        self._net_imports = 0

        self._verify_single_intervention()
        self._compute()

    def _verify_single_intervention(self):
        interventions = []
        if self.__tax != 0:
            interventions.append("tax")
        if self.__ceiling is not None:
            interventions.append("ceiling")
        if self.__floor is not None:
            interventions.append("floor")
        if self.__world_price is not None:
            interventions.append("world_price")
        if len(interventions) > 1:
            raise ValueError(
                f"Multiple interventions not supported: {interventions}"
            )

        if self.__tariff != 0 and self.__world_price is None:
            raise ValueError(
                "A nonzero tariff requires a 'world_price' to be set."
            )

    def _compute(self):
        """
        Compute the equilibrium for whichever single intervention is set.
        """
        if self.__world_price is not None:
            self._compute_small_open()
            return

        if self.__ceiling is not None:
            if self.excess_demand(self.__ceiling) > 0:
                p_star = self.__ceiling
                q_star = self.supply.q(p_star)
                self.q = q_star
                self.p = p_star
                self.__p_consumer = p_star
                self.__p_producer = p_star
                return

        if self.__floor is not None:
            if self.excess_demand(self.__floor) < 0:
                p_star = self.__floor
                q_star = self.demand.q(p_star)
                self.q = q_star
                self.p = p_star
                self.__p_consumer = p_star
                self.__p_producer = p_star
                return

        if self.__tax != 0:
            shifted = Demand(elements=[
                d.vertical_shift(-self.__tax, inplace=False)
                for d in self.demand.elements if d
            ])
            p_star, q_star = self._find_intersection(shifted, self.supply)
            self.q = q_star
            self.p = p_star
            self.__p_consumer = p_star + self.__tax
            self.__p_producer = p_star
            self.p = (self.__p_consumer, self.__p_producer)
            return

        # no intervention => free market eq
        p_star, q_star = self._find_intersection(self.demand, self.supply)
        self.q = q_star
        self.p = p_star
        self.__p_consumer = p_star
        self.__p_producer = p_star

    def _compute_small_open(self):
        """
        If ``world_price`` is set, compute the small open economy equilibrium
        and determine if the country is an importer or exporter.
        """
        # find autarky eq for reference
        p_aut, q_aut = self._find_intersection(self.demand, self.supply)
        # compare world_price to p_aut
        if self.__world_price < p_aut:
            # importer
            self._importer = True
            dom_price = np.min([p_aut, self.__world_price + self.__tariff])
        elif self.__world_price > p_aut:
            # exporter
            self._importer = False
            dom_price = self.__world_price
        else:
            self._importer = False
            dom_price = self.__world_price

        Qd = self.demand.q(dom_price)
        Qs = self.supply.q(dom_price)
        self.q = Qd  # really two quantities but using demand q
        self.p = dom_price
        self.__p_consumer = dom_price
        self.__p_producer = dom_price
        self._net_imports = Qd - Qs

    def _find_intersection(self, dcurve, scurve):
        for dpiece in dcurve.pieces:
            for spiece in scurve.pieces:
                if dpiece and spiece:
                    p_temp, q_temp = intersection(dpiece, spiece)
                    if self._valid_in_domain(dpiece, spiece, q_temp):
                        return p_temp, q_temp

        # No intersection in first quadrant
        p_max = self.demand.p(0)
        p_min = self.supply.p(0)
        # A range is better but for simplicity we return the average
        # price that will clear the market at zero
        p = 0.5*(p_max+p_min)
        return p, 0

    def _valid_in_domain(self, dpiece, spiece, q_val):
        d_dom = dpiece._domain
        s_dom = spiece._domain
        if d_dom:
            if not (d_dom[1] <= q_val <= d_dom[0]):
                return False
        if s_dom:
            if not (s_dom[0] <= q_val <= s_dom[1]):
                return False
        return True

    def excess_demand(self, p):
        return self.demand.q(p) - self.supply.q(p)

    # ================== Surplus ==================#
    @property
    def consumer_surplus(self):
        p = self.__p_consumer
        q = self.q
        return self.demand.consumer_surplus(p, q)

    @property
    def producer_surplus(self):
        p = self.__p_producer
        q = self.q - self.net_imports
        return self.supply.producer_surplus(p, q)

    @property
    def govt_revenue(self):
        # If we have a tariff
        if self.__world_price is not None and self.__tariff != 0:
            if self._importer:
                imports = max(self._net_imports, 0)
                return self.__tariff * imports
            else:
                exports = max(-self._net_imports, 0)
                return self.__tariff * exports
        # If we have a tax
        return self.__tax * self.q

    @property
    def govt_expenditure(self):
        return -self.govt_revenue

    @property
    def total_surplus(self):
        return (
            self.consumer_surplus
            + self.producer_surplus
            + self.govt_revenue
        )

    # ================== Plot ==================#
    def plot(self, ax=None, surplus=False):
        """Draw the market and its realized outcome; return the supplied axes.

        Automatic limits focus on nonnegative prices and quantities around the
        outcome. Explicit axes limits, titles and labels are retained. Demand
        and supply use distinct colors, also used by their surplus areas.
        """
        if ax is None:
            _, ax = plt.subplots()
        x_limits, y_limits = ax.get_xlim(), ax.get_ylim()
        auto_x, auto_y = ax.get_autoscalex_on(), ax.get_autoscaley_on()
        q_max, p_max = self._plot_extent()
        if not auto_x:
            q_max = max(x_limits)
        if not auto_y:
            p_max = max(y_limits)

        if surplus:
            self.plot_surplus(ax)

        # Draw only the visible economic segments, rather than stretching the
        # price scale to supply evaluated at a distant demand intercept.
        for curve, color, name in ((self.demand, DEMAND_COLOR, "D"),
                                   (self.supply, SUPPLY_COLOR, "S")):
            segments = list(_visible_curve_pieces(curve, q_max, p_max))
            for index, (quantities, prices) in enumerate(segments):
                ax.plot(quantities, prices, color=color, lw=2,
                        label=name if index == 0 else "_nolegend_", zorder=3)
            if segments:
                quantities, prices = max(segments, key=lambda segment: segment[0][-1])
                ax.annotate(name, (quantities[-1], prices[-1]),
                            xytext=(5, 4), textcoords="offset points",
                            color=color, weight="bold", annotation_clip=True)

        x = self.q
        prices = [(self.__p_consumer, "$P_c$")]
        if self.__p_consumer != self.__p_producer:
            prices.append((self.__p_producer, "$P_p$"))
        else:
            prices = [(self.__p_consumer, "")]
        guide = dict(lw=0.8, ls=(0, (3, 3)), color="0.55", zorder=1)
        ax.plot([x, x], [0, max(price for price, _ in prices)], **guide)
        for price, name in prices:
            ax.plot([0, x], [price, price], **guide)
            ax.plot([x], [price], marker="o", markersize=5.5, color="0.18",
                    markeredgecolor="white", markeredgewidth=0.8, zorder=5)
            if name:
                above = name == "$P_c$"
                ax.annotate(name, (x, price), xytext=(7, 5 if above else -5),
                            textcoords="offset points",
                            va="bottom" if above else "top", color="0.25")

        if self.__world_price is not None:
            ax.axhline(self.__world_price, color="0.45", lw=0.9,
                       linestyle="dashdot", zorder=1)
        for price, name in ((self.__ceiling, "Ceiling"), (self.__floor, "Floor")):
            if price is not None and 0 <= price <= p_max:
                ax.axhline(price, color="0.45", lw=0.9, linestyle="--", zorder=1)
                ax.annotate(name, (q_max * 0.98, price), xytext=(0, 5),
                            textcoords="offset points", ha="right", color="0.35")

        textbook_axes(ax)
        if not ax.get_xlabel():
            ax.set_xlabel("Quantity")
        if not ax.get_ylabel():
            ax.set_ylabel("Price")
        ax.set_xlim((0, q_max * 1.08) if auto_x else x_limits)
        ax.set_ylim((0, p_max * 1.08) if auto_y else y_limits)
        return ax

    def _plot_extent(self):
        """Choose finite market scales without forcing distant intercepts into view."""
        def extent(anchors, intercepts):
            anchors = [float(v) for v in anchors if np.isfinite(v) and v > 0]
            intercepts = [float(v) for v in intercepts if np.isfinite(v) and v > 0]
            anchor = max(anchors, default=max(intercepts, default=1))
            nearby = [v for v in intercepts if v <= 2.5 * anchor]
            return max([anchor * 1.2, *nearby]) if nearby else anchor * 1.6

        p_free, q_free = self._find_intersection(self.demand, self.supply)
        q_max = extent(
            [self.q, q_free, self.demand.q(self.__p_consumer),
             self.supply.q(self.__p_producer)],
            [piece.q_intercept for piece in self.demand.pieces if piece],
        )
        p_max = extent(
            [self.__p_consumer, self.__p_producer, p_free],
            [piece.intercept for piece in self.demand.pieces + self.supply.pieces
             if piece],
        )
        return q_max, p_max

    def plot_surplus(self, ax):
        """
        Shading:
          1) Consumer surplus => above p_consumer to demand
          2) Producer surplus => below p_producer to supply
            3) Government revenue => fill rectangle:
             - If a tax => from p_producer to p_consumer over [0..q]
             - If a tariff => from p_world to p_world+t (importer) or
               p_world-t to p_world (exporter), over the quantity of net
               imports or net exports.
          4) Deadweight loss =>
             - If tax/floor/ceiling => compare to no policy eq => single wedge
             - If tariff => compare to free-trade eq => two wedges
        """
        alpha = 0.5 if (self.subsidy > 0) else 1

        # 1) Consumer surplus
        self.demand.plot_surplus(
            p=self.__p_consumer, q=(0, self.q), ax=ax,
            color=CONSUMER_FILL, alpha=alpha,
        )
        # 2) Producer surplus
        q = self.q - self.net_imports
        self.supply.plot_surplus(
            p=self.__p_producer, q=(0, q), ax=ax,
            color=PRODUCER_FILL, alpha=alpha,
        )

        # 3) Government revenue shading
        self._plot_gov_revenue(ax)

        # 4) DWL shading
        self._plot_dwl(ax)

        update_axes_limits(ax)

        return ax

    def _plot_gov_revenue(self, ax):
        """
        Fill the govt revenue rectangle:
         - For a tax => from p_producer to p_consumer, over [0..q].
         - For a tariff => from p_world to p_world + t (if importer),
                           or p_world - t to p_world (if exporter),
                           over Qd-Qs or Qs-Qd.
        """
        if self.govt_revenue <= 0:
            return None

        color_rev = REVENUE_FILL
        if self.__world_price is not None and self.__tariff != 0:
            # small open economy with a tariff
            if self._importer:
                # importer => domestic price = p_world + t
                # imports = Qd - Qs
                q0 = self.supply.q(self.__world_price + self.__tariff)  # Qs
                q1 = self.demand.q(self.__world_price + self.__tariff)  # Qd
                # fill from p_world up to p_world+t, horizontally from [q0..q1]
                if q1 > q0:
                    ax.fill_between(
                        [q0, q1],
                        self.__world_price,
                        self.__world_price + self.__tariff,
                        color=color_rev
                    )
            else:
                # exporter => domestic price = p_world - t
                q0 = self.demand.q(self.__world_price - self.__tariff)
                q1 = self.supply.q(self.__world_price - self.__tariff)
                if q1 > q0:
                    # fill from p_world - t up to p_world
                    ax.fill_between(
                        [q0, q1],
                        self.__world_price - self.__tariff,
                        self.__world_price,
                        color=color_rev
                    )
        else:
            # a tax => fill from p_producer..p_consumer, over [0..q]
            pp, pc = self.__p_producer, self.__p_consumer
            if pc > pp:
                ax.fill_between([0, self.q], pp, pc, color=color_rev)

    def _plot_dwl(self, ax):
        """
        If a tariff => compare to free trade => 2 wedges
        If a tax/floor/ceiling => compare to no policy eq => 1 wedge
        """
        if self.__world_price is not None:
            if self.__tariff != 0:
                self._plot_tariff_dwl(ax)
        else:
            self._plot_closed_dwl(ax)

    def _plot_closed_dwl(self, ax):
        """
        For tax/floor/ceiling, compare to the no-policy equilibrium and
        fill a single wedge in red.
        """
        # find free market eq (no policy)
        fm = Equilibrium(self.demand, self.supply)
        q_star = fm.q
        q_new = self.q
        if q_new == q_star:
            return
        left, right = sorted((q_new, q_star))
        # Intersect the two piece partitions so each lost (or excess) trade is
        # shaded once, exactly between its marginal benefit and marginal cost.
        for demand in self.demand.pieces:
            if demand is None:
                continue
            for supply in self.supply.pieces:
                if supply is None:
                    continue
                lo = max(left, min(demand._domain), min(supply._domain))
                hi = min(right, max(demand._domain), max(supply._domain))
                if hi > lo:
                    ax.fill_between([lo, hi], [demand(lo), demand(hi)],
                                    [supply(lo), supply(hi)],
                                    color=DWL_FILL, zorder=0.5)

    def _plot_tariff_dwl(self, ax):
        """
        Compare the new outcome (tariff>0) to the free-trade equilibrium
        (same ``world_price``, ``tariff`` = 0) and shade the under-consumption
        and over-production wedges in red.
        """
        ft = Equilibrium(
            demand=self.demand,
            supply=self.supply,
            tax=0,
            ceiling=None,
            floor=None,
            world_price=self.__world_price,
            tariff=0
        )
        # If no difference in Q => no wedge
        if abs(ft.q - self.q) < 1e-9:
            return

        Qd_old = ft.demand.q(self.__world_price)  # Qd under free trade
        Qs_old = ft.supply.q(self.__world_price)

        Qd_new = self.q
        Qs_new = self.supply.q(self.p)

        Pw = self.__world_price
        red = DWL_FILL

        if ft._importer:
            # under-consumption wedge => Qd_new..Qd_old
            if Qd_old > Qd_new:
                # use fine grid in case of piece-wise demand
                q_grid = np.linspace(Qd_new, Qd_old, 1000)
                p_above = [self.demand.p(q) for q in q_grid]
                ax.fill_between(
                    x=q_grid,
                    y1=p_above,
                    y2=Pw,
                    color=red,
                )
            # over-production wedge => Qs_old..Qs_new
            if Qs_new > Qs_old:
                q_grid = np.linspace(Qs_old, Qs_new, 1000)
                p_supply = np.array([self.supply.p(qq) for qq in q_grid])
                ax.fill_between(
                    x=q_grid,
                    y1=p_supply,
                    y2=Pw,
                    color=red,
                )

    # ================== Properties & Setters =================#
    @property
    def tax(self):
        return self.__tax

    @tax.setter
    def tax(self, val):
        if val != 0 and any([
            self.__ceiling is not None,
            self.__floor is not None,
            self.__world_price is not None
        ]):
            raise ValueError("Multiple interventions not supported.")
        self.__tax = val
        self._verify_single_intervention()
        self._compute()

    @property
    def subsidy(self):
        return -self.__tax

    @subsidy.setter
    def subsidy(self, val):
        if val != 0 and any([
            self.__ceiling is not None,
            self.__floor is not None,
            self.__world_price is not None
        ]):
            raise ValueError("Multiple interventions not supported.")
        self.__tax = -val
        self._verify_single_intervention()
        self._compute()

    @property
    def ceiling(self):
        return self.__ceiling

    @ceiling.setter
    def ceiling(self, val):
        if val is not None and any([
            self.__tax != 0,
            self.__floor is not None,
            self.__world_price is not None
        ]):
            raise ValueError("Multiple interventions not supported.")
        self.__ceiling = val
        self._verify_single_intervention()
        self._compute()

    @property
    def floor(self):
        return self.__floor

    @floor.setter
    def floor(self, val):
        if val is not None and any([
            self.__tax != 0,
            self.__ceiling is not None,
            self.__world_price is not None
        ]):
            raise ValueError("Multiple interventions not supported.")
        self.__floor = val
        self._verify_single_intervention()
        self._compute()

    @property
    def world_price(self):
        return self.__world_price

    @world_price.setter
    def world_price(self, val):
        if val is not None and any([
            self.__tax != 0,
            self.__ceiling is not None,
            self.__floor is not None
        ]):
            raise ValueError("Multiple interventions not supported.")
        self.__world_price = val
        self._verify_single_intervention()
        self._compute()

    @world_price.deleter
    def world_price(self):
        self.__world_price = None
        self.__tariff = 0
        self._verify_single_intervention()
        self._compute()

    @property
    def tariff(self):
        return self.__tariff

    @tariff.setter
    def tariff(self, val):
        if val != 0 and self.__world_price is None:
            raise ValueError("A nonzero tariff requires a 'world_price'.")
        if val < 0:
            raise ValueError(
                "Import subsidies (negative tariffs) are not supported."
            )
        self.__tariff = val
        self._verify_single_intervention()
        self._compute()

    @property
    def p_consumer(self):
        return self.__p_consumer

    @property
    def p_producer(self):
        return self.__p_producer

    @property
    def net_imports(self):
        return self._net_imports

    @property
    def imports(self):
        net = self._net_imports
        return net if net > 0 else 0

    @property
    def exports(self):
        net = self._net_imports
        return -net if net < 0 else 0

    @property
    def dwl(self):
        free_market_surplus = Equilibrium(
                                self.demand,
                                self.supply,
                                world_price=self.world_price).total_surplus
        realized_surplus = self.total_surplus
        return free_market_surplus - realized_surplus

    def __repr__(self):
        return f"Price: {self.p}\nQuantity: {self.q}"


class Market(Equilibrium):
    """
    Markets tend toward equilibrium.
    Subclass for convenience usage:

    m = Market(D, S)
    m.world_price = 4
    m.tariff = 1
    m.plot(surplus=True)

    m2 = Market(D, S)
    m2.ceiling = 3
    m2.plot(surplus=True)
    """
    def __init__(
            self,
            demand: Demand,
            supply: Supply,
            tax=0,
            ceiling=None,
            floor=None,
            world_price=None,
            tariff=0
    ):
        super().__init__(
            demand=demand,
            supply=supply,
            tax=tax,
            ceiling=ceiling,
            floor=floor,
            world_price=world_price,
            tariff=tariff
        )


class LongRunCompetitiveEquilibrium:
    """Long-run perfectly competitive equilibrium with identical firms."""

    def __init__(self, demand: Demand, total_cost):
        """Compute long-run equilibrium for a competitive market."""
        self.total_cost = total_cost
        self.demand = demand

        # In long-run competitive equilibrium price equals breakeven price.
        self.p = self.total_cost.breakeven_price()

        # Quantity each firm produces at the breakeven price.
        self.firm_q = self.total_cost.efficient_scale()

        # Total quantity demanded at the equilibrium price.
        self.market_q = self.demand.q(self.p)

        # Number of identical firms in the market.
        self.n_firms = self.market_q / self.firm_q

    def plot(self, fig=None):
        """Plot firm and market diagrams side by side."""

        if fig is None:
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

        return fig
