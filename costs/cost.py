import matplotlib.pyplt as plt
import numpy as np

from marginal_cost import MarginalCost


class Cost:
    def __init__(self, constant, linear, quadratic, currency="$", reciprocal=0):
        """Create a quadratic cost curve,
        constant + linear*q + quadratic*q^2. Reciprocal just for average costs"""

        self.constant = constant
        self.linear = linear
        self.quadratic = quadratic
        self.currency = currency
        self.reciprocal = reciprocal

    def cost(self, q):
        """Return cost at quantity q."""
        if self.reciprocal == 0:  # allows for q = 0 calcs
            return self.constant + self.linear * q + self.quadratic * (q ** 2)
        return (
            self.constant
            + self.linear * q
            + self.quadratic * (q ** 2)
            + self.reciprocal * (1 / q)
        )

    def variable_cost(self):
        """Return Cost object less fixed costs."""
        return Cost(
            constant=0,
            linear=self.linear,
            quadratic=self.quadratic,
            currency=self.currency,
        )

    def marginal_cost(self):
        """Finds marginal cost, assuming cost is quadratic."""
        return MarginalCost(
            constant=self.linear,
            linear=2 * self.quadratic,
            quadratic=0,
            currency=self.currency,
        )

    def average_cost(self):
        return Cost(
            constant=self.linear,
            linear=self.quadratic,
            quadratic=0,
            reciprocal=self.constant,
            currency=self.currency,
        )

    def efficient_scale(self):
        """Find q that minimizes average cost."""

        # Avg Cost = constant/q + linear + quadratic * q
        # d/dq Avg Cost = - constant/q**2 + quadratic = 0
        # q**2 = constant / quadratic

        return np.sqrt(self.constant / self.quadratic)

    def breakeven_price(self):
        """Assume perfect competition and find price such that economic profit is zero."""

        # find MC = ATC
        return self.marginal_cost().cost(self.efficient_scale())

    def shutdown_price(self):
        """Assume perfect competition and find price such that total revenue = total variable cost."""

        var = self.variable_cost()
        return var.marginal_cost().cost(var.efficient_scale())

    def plot(self, ax=None, max_q=100, label=None, min_plotted_q=0.1):
        """Plot the cost curve.
        min_plotted_q is used when the cost goes to infinity as q->0 to keep y-limits from also going to infinity."""
        if ax == None:
            ax = plt.gca()

        x_vals = np.linspace(0, max_q, max_q * 5 + 1)
        if self.reciprocal != 0:
            x_vals = x_vals[x_vals >= min_plotted_q]
        y_vals = [self.cost(q) for q in x_vals]

        ax.plot(x_vals, y_vals, label=label)
        ax.set_xlabel("Quantity")
        ax.set_ylabel("Cost ({})".format(self.currency))

        # Make textbook-style plot window
        ax.spines["left"].set_position("zero")
        ax.spines["bottom"].set_position("zero")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
