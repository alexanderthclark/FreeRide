import matplotlib.pyplot as plt

from curve import Curve


class Supply(Curve):
    def __init__(self, intercept, slope, inverse=True):
        """Create supply curve with intercept and slope, specifying inverse form or not.
        Inverse if P(Q), as opposed to Q(P)."""
        Curve.__init__(self, intercept, slope, inverse)

    def producer_surplus(self, p):

        qs = self.q(p)

        if qs <= 0:
            return 0

        if self.intercept >= 0:

            tri_height = -self.intercept + p
            tri_base = qs

            ps1 = 0.5 * tri_base * tri_height

            return ps1

        # get rectangle
        rect_w = self.q_intercept
        rect_h = p
        rect_area = rect_w * rect_h

        tri_area = 0.5 * (qs - rect_w) * p

        return tri_area + rect_area

    def plot_surplus(self, demand, ax=None, annotate=False):

        # p,q = self.equilibrium(demand)
        if ax == None:
            ax = plt.gca()
        # CS region
        # cs_plot = ax.fill_between([0,q], y1 = [demand.intercept, p], y2 = p,  alpha = 0.1)

        # fix later for negative
        ps_plot = ax.fill_between(
            [0, q], y1=[self.intercept, p], y2=p, color="C1", alpha=0.1
        )

        # if annotate:
        #   cs = demand.consumer_surplus(p)
        #  ps = self.producer_surplus(p)
