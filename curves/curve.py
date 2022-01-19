import numpy as np
import matplotlib.pyplot as plt


class Curve:
    def __init__(self, intercept, slope, inverse=True):
        """Create curve with intercept and slope, specifying inverse form or not.
        Inverse if P(Q), as opposed to Q(P)."""

        if inverse:
            self.intercept = intercept
            self.slope = slope
            if slope != 0:
                self.q_intercept = -intercept / slope
            else:
                self.q_intercept = np.nan

        else:
            self.slope = 1 / slope
            self.intercept = -intercept / slope
            if slope != 0:
                self.q_intercept = -self.intercept / self.slope
            else:
                self.q_intercept = np.nan

    def q(self, p):
        """Quantity demanded or supplied at price p."""
        return (self.intercept / (-self.slope)) + (p / self.slope)

    def p(self, q):
        """Price when quantity demanded/supplied is at q."""
        return self.intercept + self.slope * q

    def vertical_shift(self, delta):
        """Shift curve vertically by amount delta. Shifts demand curve to the right.
        Shifts supply curve to the left."""
        self.intercept += delta
        if self.slope != 0:
            self.q_intercept = -self.intercept / self.slope

    def horizontal_shift(self, delta):
        """Shift curve horizontally by amount delta. Positive values are shifts to the right."""
        equiv_vert = delta * -self.slope
        self.intercept += equiv_vert
        if self.slope != 0:
            self.q_intercept = -self.intercept / self.slope

    def equilibrium(self, other_curve):
        """Returns a tuple (p, q). Allows for negative prices or quantities."""

        v1 = np.array([1, -self.slope])
        v2 = np.array([1, -other_curve.slope])

        b = self.intercept, other_curve.intercept

        A = np.matrix((v1, v2))
        b = np.matrix(b).T

        x = np.linalg.inv(A) * b
        x = x.squeeze()
        return x[0, 0], x[0, 1]  # p, q

    def plot(self, ax=None, color="black", linewidth=2, max_q=10, clean=True):

        if ax == None:
            ax = plt.gca()

        # core plot
        q_ = self.q_intercept
        if np.isnan(q_):  # if slope is 0
            q_ = 10 ** 10
        x2 = np.max([q_, max_q])
        y2 = self.intercept + self.slope * x2

        xs = np.linspace(0, x2, 2)
        ys = np.linspace(self.intercept, y2, 2)

        ax.plot(xs, ys, color=color, linewidth=linewidth)

        if clean:
            ax.spines["left"].set_position("zero")
            ax.spines["bottom"].set_position("zero")
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)

    def equilibrium_plot(
        self, other_curve, ax=None, linewidth=2, annotate=False, clean=True
    ):
        """Plot the intersection of two curves. This can't handle taxes or other interventions."""
        if ax == None:
            fig, ax = plt.gcf(), plt.gca()
        # else:
        #   global ax
        for curve in self, other_curve:
            curve.plot(ax=ax, linewidth=linewidth)

        ax.set_ylabel("Price")
        ax.set_xlabel("Quantity")

        # dashed lines around market price and quantity
        p, q = self.equilibrium(other_curve)
        ax.plot([0, q], [p, p], linestyle="dashed", color="C0")
        ax.plot([q, q], [0, p], linestyle="dashed", color="C0")
        ax.plot([q], [p], marker="o")

        # annotation on the plot
        if annotate:
            s = " $p = {:.1f}, q = {:.1f}$".format(p, q)
            ax.text(q, p, s, ha="left", va="center")

        if clean:
            self.equilibrium_plot_cleaner(other_curve)

    # elasticity section

    def price_elasticity(self, p):
        """Find point price elasticity given a price."""

        q = self.q_intercept + (1 / self.slope) * p
        e = (p / q) * (1 / self.slope)
        return e

    def midpoint_elasticity(self, p1, p2):
        """Find price elasticity between two prices, using the midpoint formula."""
        mean_p = 0.5 * p1 + 0.5 * p2
        return self.price_elasticity(mean_p)

    def equilibrium_plot_cleaner(self, other_curve, ax=None):

        if ax == None:
            ax = plt.gca()

        # Make textbook-style plot window
        ax.spines["left"].set_position("zero")
        ax.spines["bottom"].set_position("zero")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        # customize limits

        # P-axis intercepts (y-axis)
        min_int = np.min([self.intercept, other_curve.intercept])
        max_int = np.max([self.intercept, other_curve.intercept])

        min_y = np.min([-1, min_int])
        max_y = np.max([0, max_int * 1.1])
        ax.set_ylim(min_y, max_y)

        # Q-axis intercepts (x-axis)
        # min_int = np.min([self.q_intercept, other_curve.q_intercept])
        # max_int = np.max([self.q_intercept, other_curve.q_intercept])

        # min_x = np.min([-1, min_int])
        # max_x = np.max([0, max_int*1.1])
        # ax.set_xlim(min_x, max_x)

    def externality(self, externality, is_signed=True, is_positive=None):
        """Creates marginal social cost or benefit given a Curve and externality."""

        is_demand = self.slope < 0  # figure out if this is supply or demand curve

        if is_positive == True:  # add to demand/MSB, substract from supply MSC
            if is_demand:
                externality = np.abs(externality)
            else:
                externality = -np.abs(externality)
        if is_positive == False:
            if is_demand:
                externality = -np.abs(externality)
            else:
                externality = +np.abs(externality)

        social_curve = Curve(
            self.intercept + self.externality, self.slope, inverse=True
        )
        return social_curve
