import numpy as np

from cost import Cost
from curves.supply_curve import Supply


class MarginalCost(Cost):
    def __init__(self, constant, linear, quadratic=0, currency="$"):
        """Create demand curve with intercept and slope, specifying inverse form or not.
        Inverse if P(Q), as opposed to Q(P)."""
        Cost.__init__(self, constant, linear, quadratic, currency)

    def q(self, p):

        # p = self.constant + self.linear * q + self.quadratic * q**2
        # self.quadratic * q**2 + self.linear * q + self.constant - p
        roots = np.roots([self.quadratic, self.linear, self.constant - p])

        if self.quadratic != 0:
            print("No quadratic MC please.")

        root = roots[0]

        return root

    def supply(self):
        """Convert to a supply object"""
        return Supply(intercept=self.constant, slope=self.linear)
