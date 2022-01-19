from linear_constraint import LinearConstraint


class PPF(LinearConstraint):
    def __init__(
        self,
        p1=None,
        p2=None,
        max1=None,
        max2=None,
        endowment=1,
        good_names=["Good 1", "Good 2"],
    ):
        """Create demand curve with intercept and slope, specifying inverse form or not.
        Inverse if P(Q), as opposed to Q(P)."""
        LinearConstraint.__init__(self, p1, p2, max1, max2, endowment, good_names)
