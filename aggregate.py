import numpy as np
import matplotlib.pyplot as plt


class Aggregate:
    def __init__(self, curve_array=None, *args):
        """Create aggregated supply or demand curves. Arguments must be all supply or all demand."""

        # self.__dict__.update(('curve' + str(k), v) for k, v in enumerate(curve_array))
        if curve_array == None:
            curve_array = list(args)
        self.curve_array = curve_array
        slopes = sorted([x.slope for x in self.curve_array])
        self.is_demand = slopes[0] < 0
        self.is_supply = not self.is_demand

    def q(self, p):
        """Find aggregate quantity at price p."""
        total_q = 0
        for curve in self.curve_array:
            total_q += np.max([0, curve.q(p)])
        return total_q

    def productive_efficiency(self, Q):
        """Find q1, ..., qn and p at total quantity Q."""

        # distributive/productive efficiency requires MB = MB or MC = MC
        n = len(self.curve_array)

        # set up linear system to solve for q1, ..., qn, and MC.
        # q1 + q2 + ... + qn + 0*MC = Q
        # mc1 = MC
        # mc2 = MC

        accounting = np.concatenate([np.ones(n), np.array([0])])

        #
        b_vec = np.array([0] + [])
        from itertools import combinations

        row_vectors = [accounting]
        b_values = [Q]
        for key, curve in enumerate((self.curve_array)):

            # 0 + slope*q_curve + 0 - MC =  - curve.intercept
            c_vec = np.concatenate(
                [
                    np.zeros(key),
                    curve.slope * np.ones(1),
                    np.zeros(n - key - 1),
                    -1 * np.ones(1),
                ]
            )

            row_vectors.append(c_vec)
            b_values.append(-curve.intercept)

        A = np.matrix(row_vectors)
        b = np.matrix(b_values).T

        # return A, b
        x = np.linalg.inv(A) * b
        x = x.squeeze()
        return x[0, :-1], x[0, -1]  # q1 ... qn, MC

        # all
        # total_p = 0
        # for curve in self.curve_array:
        #    total_p += np.max([0,curve.p(q)])
        # return total_p

    def distributive_efficiency(self, Q):
        return self.productive_efficiency(Q)

    def plot(self, ax=None, color="black", linewidth=2, max_q=10, clean=True):

        if ax == None:
            ax = plt.gca()

        intercepts = sorted([x.intercept for x in self.curve_array])
        slopes = sorted([x.slope for x in self.curve_array])

        if np.min(slopes) < 0:  # demand curves

            max_y = intercepts[-1]

            y_vec = np.linspace(0, max_y, 1000)
            x_vec = [self.q(y) for y in y_vec]

            ax.plot(x_vec, y_vec, color=color, linewidth=linewidth)
        else:  # supply curve

            max_y = intercepts[-1] * 2
            y_vec = np.linspace(0, np.max([10, max_y * 2]), 1000)
            x_vec = [self.q(y) for y in y_vec]

            ax.plot(x_vec, y_vec, color=color, linewidth=linewidth)
        if clean:
            self.plot_clean()

    def kinks(self):
        """Return p, q pairs for kink locations."""
        intercepts = sorted([x.intercept for x in self.curve_array])
        pairs = list()

        if self.is_demand == True:
            relevant_intercepts = intercepts[:-1]
        else:
            relevant_intercepts = intercepts[1:]
        for intercept in relevant_intercepts:
            # get q
            q = self.q(intercept)
            pair = [(intercept, q)]
            pairs += pair
        return pairs

    def plot_clean(self, ax=None):

        if ax == None:
            ax = plt.gca()

        kink_list = self.kinks()

        ys = [pair[0] for pair in kink_list]  # p values
        xs = [pair[1] for pair in kink_list]  # q values

        intercepts = sorted([x.intercept for x in self.curve_array])

        important_x = xs + [self.q(0)]
        important_x = [x for x in sorted(important_x) if x > 0]

        important_y = ys + intercepts
        important_y = [0] + [y for y in sorted(important_y) if y > 0]

        ax.set_yticks(important_y)
        ax.set_xticks(important_x)

        # Make textbook-style plot window
        ax.spines["left"].set_position("zero")
        ax.spines["bottom"].set_position("zero")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    def equilibrium(self, other, price_guess=1, tolerance=0.05):
        """Find market clearing price and quantity with another aggregate or curve object."""

        surplus = self.q(price_guess) - other.q(price_guess)
        if self.is_demand:
            excess_demand = surplus
        else:
            excess_demand = -surplus

        has_cycled = False
        counter, last_counter = 0, 0
        scale = 1
        while np.abs(excess_demand) > tolerance:

            if excess_demand > 0:

                price_guess += tolerance * scale

                if counter > last_counter:
                    has_cycled = True
                    scale *= 0.5
                counter += 1
                last_counter = counter
            else:  # must be strictly negative bc while condition

                price_guess -= tolerance
                counter += 1
            # print(price_guess, surplus)
            surplus = self.q(price_guess) - other.q(price_guess)
            if self.is_demand:
                excess_demand = surplus
            else:
                excess_demand = -surplus

        # get points on supply and demand
        # use local linearity to find exact solution
        # p1 = price_guess, self.q(price_guess)
        # p2 = price_guess, self.q(price_guess)

        # returns point on the object on which the method is called
        return price_guess, self.q(price_guess)

    def equilibrium_plot(self, other, ax=None):
        if ax == None:
            ax = plt.gca()

        # plot curves
        self.plot(ax)
        other.plot(ax)

        # add equilibrium things
        p, q = self.equilibrium(other)

        # reset ticks and such

        if type(other) == Aggregate:

            kink_list = self.kinks() + other.kinks()
        else:
            kink_list = self.kinks()

        ys = [pair[0] for pair in kink_list]  # p values
        xs = [pair[1] for pair in kink_list]  # q values

        intercepts = sorted([x.intercept for x in self.curve_array])

        important_x = xs + [self.q(0)] + [q]
        important_x = [x for x in sorted(important_x) if x > 0]

        important_y = ys + intercepts + [p]
        important_y = [0] + [y for y in sorted(important_y) if y > 0]

        # ax.set_yticks(important_y)
        # ax.set_xticks(important_x)

        # label p and q
        ax.plot([0, q], [p, p], linestyle="dashed", color="C0")
        ax.plot([q, q], [0, p], linestyle="dashed", color="C0")

        # set axes limits
        if self.is_demand:
            self.plot_clean()
            xmax = self.q(0)
            ymax = ax.get_yticks()[-1]
        else:
            # other.plot_clean()
            xmax = other.q(0)
            ymax = other.get_yticks()[-1]

        ax.set_xlim(0, xmax * 1.04)
        ax.set_ylim(0, ymax * 1.04)

        ax.set_yticks(important_y)
        ax.set_xticks(important_x)
