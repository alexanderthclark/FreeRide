import matplotlib.pyplt as plt
import numpy as np


class LinearConstraint:
    def __init__(
        self,
        p1=None,
        p2=None,
        max1=None,
        max2=None,
        endowment=1,
        good_names=["Good 1", "Good 2"],
    ):
        """Create a linear budget line or PPF."""

        self.good_names = good_names
        if p1 != None:
            self.p1 = p1
            self.max1 = endowment / p1
        elif max1 != None:
            self.p1 = endowment / max1
            self.max1 = max1
        else:
            print("add error handling")

        if p2 != None:
            self.p2 = p2
            self.max2 = endowment / p2

        elif max2 != None:
            self.p2 = endowment / max2
            self.max2 = max2
        else:
            print("add error handling")

        self.endowment = endowment

    def plot(self, ax=None, linewidth=2):
        if ax == None:
            ax = plt.gca()

        ax.plot([0, self.max1], [self.max2, 0], linewidth=linewidth)

        ax.set_xlabel(self.good_names[0])
        ax.set_ylabel(self.good_names[1])

        if True:
            ax.spines["left"].set_position("zero")
            ax.spines["bottom"].set_position("zero")
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
