import matplotlib.pyplot as plt

from curve import Curve


class Demand(Curve):
    """Creates linear, downward-sloping demand curve."""

    def __init__(self, intercept, slope, inverse=True):
        """Create demand curve with intercept and slope, specifying inverse form or not.
        Inverse if P(Q), as opposed to Q(P)."""
        Curve.__init__(self, intercept, slope, inverse)

    def consumer_surplus(self, p):
        """Calculate consumer surplus given a price p."""
        tri_height = self.intercept - p
        tri_base = self.q(p)

        return 0.5 * tri_base * tri_height

    def plot_surplus(self, p, ax=None):
        """Plot consumer surplus."""

        if ax == None:
            ax = plt.gca()

        # CS region
        cs_plot = ax.fill_between([0, q], y1=[self.intercept, p], y2=p, alpha=0.1)
