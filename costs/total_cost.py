import matplotlib.pyplot as plt

from cost import Cost


class TotalCost(Cost):
    """Creates linear, downward-sloping demand curve."""

    def __init__(self, constant, linear, quadratic):
        """Create demand curve with intercept and slope, specifying inverse form or not.
        Inverse if P(Q), as opposed to Q(P)."""
        Cost.__init__(self, constant, linear, quadratic)

    def long_run_plot(self, ax=None):

        ac = self.average_cost()
        mc = self.marginal_cost()

        if ax == None:
            ax = plt.gca()

        # find price and q
        p, q = self.breakeven_price(), self.efficient_scale()

        max_q = int(2 * q)
        ac.plot(ax, label="LRAC", max_q=max_q)
        mc.plot(ax, label="MC", max_q=max_q)

        ax.plot([0, q], [p, p], linestyle="dashed", color="gray")
        ax.plot([q, q], [0, p], linestyle="dashed", color="gray")
        ax.plot([q], [p], marker="o")
        ax.set_xlim(0, max_q)
        ax.legend()

    def cost_profit_plot(self, p, ax=None, items=["tc", "tr", "profit"]):
        if ax == None:
            ax = plt.gca()

        items = [str(x).lower() for x in items]

        # set p = mc
        mc = self.marginal_cost()
        q = mc.q(p)

        # plot AC and MC
        self.average_cost().plot(label="ATC")
        mc.plot(label="MC")

        # plot price and quantity
        ax.plot([0, q], [p, p], linestyle="dashed", color="gray")
        ax.plot([q, q], [0, p], linestyle="dashed", color="gray")
        ax.plot([q], [p], marker="o")

        atc_of_q = self.average_cost().cost(q)

        if "profit" in items:
            # profit
            profit = q * (p - atc_of_q)
            if profit > 0:
                col = "green"
            else:
                col = "red"
            ax.fill_between(
                [0, q], atc_of_q, p, color=col, alpha=0.3, label=r"$\pi$", hatch="\\"
            )

        if "tc" in items:
            # total cost
            ax.fill_between(
                [0, q],
                0,
                atc_of_q,
                facecolor="yellow",
                alpha=0.1,
                label="TC",
                hatch="/",
            )

        if "tr" in items:
            ax.fill_between(
                [0, q], 0, p, facecolor="blue", alpha=0.1, label="TR", hatch="+"
            )

        ax.set_ylim(0, p * 1.5)
        ax.set_xlim(0, q * 1.5)
        ax.legend()
