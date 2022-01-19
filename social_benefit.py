import numpy as np
import matplotlib.pyplot as plt


class SocialBenefit:
    def __init__(self, demand_array, *args):
        """Performs vertical summation of demand curves or Marginal Social Benefit curve.
        For public goods."""
        if demand_array == None:
            demand_array = list(args)
        self.demand_array = demand_array

    def marginal_social_benefit(self, q):
        """Vertical summation of demand curves"""
        benefit = 0
        for curve in self.demand_array:
            benefit += np.max([0, curve.p(q)])
        return benefit

    def plot(self, ax=None, color="black", linewidth=2, max_q=10, clean=True):
        if ax == None:
            ax = plt.gca()

        intercepts = sorted([x.q_intercept for x in self.demand_array])
        slopes = sorted([x.slope for x in self.demand_array])

        max_x = intercepts[-1]

        x_vec = np.linspace(0, max_x, 1000)
        y_vec = [self.msb(x) for x in x_vec]

        ax.plot(x_vec, y_vec, color=color, linewidth=linewidth)

        if clean:
            # Make textbook-style plot window
            ax.spines["left"].set_position("zero")
            ax.spines["bottom"].set_position("zero")
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)

    def efficient_outcome(self, other, quantity_guess=1, tolerance=0.05):
        """Find MSB and quantity with another aggregate or curve object. MSB as price does not give the
        corresponding quantity."""

        # MSB - MSC
        allocative_ineff = (
            self.msb(quantity_guess) - other.productive_efficiency(quantity_guess)[1]
        )

        has_cycled = False
        counter, last_counter = 0, 0
        scale = 1
        while np.abs(allocative_ineff) > tolerance:

            if allocative_ineff > 0:
                # higher benefit than cost so increase quantity

                quantity_guess += tolerance * scale

                if counter > last_counter:
                    has_cycled = True
                    scale *= 0.5
                counter += 1
                last_counter = counter
            else:  # must be strictly negative bc while condition
                # lower quantity
                quantity_guess -= tolerance
                counter += 1
            # print(price_guess, surplus)
            allocative_ineff = (
                self.msb(quantity_guess)
                - other.productive_efficiency(quantity_guess)[1]
            )

        return self.msb(quantity_guess), quantity_guess

    def private_outcome(self, mc_array):
        """Find private outcome. MC array must be ordered in alignment with demand_array."""

        # linear system of eq, solve for q1, qn
        # MB - MC = 0

        row_vecs, b_values = list(), list()
        n = len(mc_array)  # number of agents
        for key, demand_cost in enumerate(zip(self.demand_array, mc_array)):
            demand = demand_cost[0]
            cost = demand_cost[1]

            cost_piece = np.concatenate(
                [np.zeros(key), (-1 * cost.linear) * np.ones(1), np.zeros(n - key - 1)]
            )

            benefit_piece = demand.slope * np.ones(n)
            row_vec = cost_piece + benefit_piece
            b_value = cost.constant - demand.intercept

            row_vecs.append(row_vec)
            b_values.append(b_value)

        A = np.matrix(row_vecs)
        b = np.matrix(b_values).T

        # return A, b
        x = np.linalg.inv(A) * b
        x = x.squeeze()
        return x  # q decisions

    def private_outcome_residual_demand_plots(self, mc_array, fig=None):
        """Plot demand residual demand."""

        q_vec = self.private_outcome(mc_array)
        q_vec = np.array(q_vec).squeeze()
        Q = q_vec.sum()

        if fig == None:
            fig = plt.gcf()

        n = len(mc_array)
        n_rows = n
        counter = 1
        for key, demand in enumerate(self.demand_array):

            supply = mc_array[key].supply()
            residual_Q = Q - q_vec[key]  # q_{-i}

            demand.horizontal_shift(-residual_Q)

            ax = fig.add_subplot(n_rows, 2, counter)
            demand.equilibrium_plot(supply, ax=ax)
            ax.set_xlabel("Private Contribution")
            ax.set_title("Residual Demand and Private Production")
            xlim_max = ax.get_xlim()[1]
            ax.set_xlim(0, xlim_max)
            ylim_max = ax.get_ylim()[1]
            ax.set_ylim(0, ylim_max)

            sharex = None
            if key > 0:
                sharex = ax2  # previous plot above
            ax2 = fig.add_subplot(n_rows, 2, counter + 1, sharey=ax, sharex=sharex)
            demand.horizontal_shift(residual_Q)  # shift back
            demand.plot(ax=ax2)
            ax2.plot([Q, Q], [0, demand.p(Q)], linestyle="dashed")
            ax2.set_xlabel("Public Provision")
            ax2.set_title("Demand and Total Consumption")

            counter += 2

        plt.tight_layout()

    def msb(self, q):
        """Abbreviation method for marginal_social_benefit()."""
        return self.marginal_social_benefit(q)
