"""Game theory utilities."""

import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple, Optional, Sequence

class Game:
    """Simple two-player game.

    Parameters
    ----------
    payoffs1 : array-like
        Payoff matrix for player 1. Rows correspond to player 1 actions and
        columns correspond to player 2 actions.
    payoffs2 : array-like
        Payoff matrix for player 2 with the same shape as ``payoffs1``.
    """

    def __init__(self, payoffs1, payoffs2):
        self.payoffs1 = np.asarray(payoffs1, dtype=float)
        self.payoffs2 = np.asarray(payoffs2, dtype=float)

        if self.payoffs1.shape != self.payoffs2.shape:
            raise ValueError("Payoff matrices must have the same shape")
        if self.payoffs1.ndim != 2:
            raise ValueError("Payoff matrices must be 2-dimensional")

    @property
    def shape(self) -> Tuple[int, int]:
        return self.payoffs1.shape

    def best_response(self, profile: Tuple[int, int]) -> List[int]:
        """Return a best response profile to ``profile``.

        Parameters
        ----------
        profile : tuple of int
            Current actions ``(i, j)`` for players A and B.
        """
        i, j = profile
        br_i = i
        best_payoff_i = self.payoffs1[i, j]
        for alt in range(self.shape[0]):
            payoff = self.payoffs1[alt, j]
            if payoff > best_payoff_i:
                best_payoff_i = payoff
                br_i = alt

        br_j = j
        best_payoff_j = self.payoffs2[i, j]
        for alt in range(self.shape[1]):
            payoff = self.payoffs2[i, alt]
            if payoff > best_payoff_j:
                best_payoff_j = payoff
                br_j = alt

        return [br_i, br_j]

    def best_responses(self) -> Tuple[List[List[int]], List[List[int]]]:
        """Return best responses for each pure strategy profile."""
        rows, cols = self.shape
        br1 = []
        br2 = []
        for j in range(cols):
            col = self.payoffs1[:, j]
            max_val = col.max()
            br1.append([i for i in range(rows) if col[i] == max_val])
        for i in range(rows):
            row = self.payoffs2[i, :]
            max_val = row.max()
            br2.append([j for j in range(cols) if row[j] == max_val])
        return br1, br2

    def nash_equilibria(self) -> List[Tuple[int, int]]:
        """Compute pure strategy Nash equilibria."""
        br1, br2 = self.best_responses()
        eqs = []
        for j, rows in enumerate(br1):
            for i in rows:
                if j in br2[i]:
                    eqs.append((i, j))
        return eqs

    def nash(self) -> List[Tuple[int, int]]:
        """Alias for :meth:`nash_equilibria`."""
        return self.nash_equilibria()

    def mixed_strategy_equilibrium(self) -> Tuple[float, float]:
        """Return mixed strategy equilibrium for 2x2 games."""
        if self.shape != (2, 2):
            raise ValueError("Mixed strategy solver only implemented for 2x2 games")

        a, b = self.payoffs1[0]
        c, d = self.payoffs1[1]
        e, f = self.payoffs2[0]
        g, h = self.payoffs2[1]

        denom_q = a - b - c + d
        denom_p = e - f - g + h
        if denom_q == 0 or denom_p == 0:
            raise ValueError("Game has no mixed strategy equilibrium")

        q = (d - b) / denom_q
        p = (h - g) / denom_p
        return p, q

    def weakly_dominant_strategies(self) -> dict:
        """Return weakly dominant strategies for both players."""

        rows, cols = self.shape
        dom1 = set()
        dom2 = set()

        for a in range(rows):
            dominates = True
            strictly = False
            for b in range(rows):
                if a == b:
                    continue
                for j in range(cols):
                    if self.payoffs1[a, j] < self.payoffs1[b, j]:
                        dominates = False
                        break
                    if self.payoffs1[a, j] > self.payoffs1[b, j]:
                        strictly = True
                if not dominates:
                    break
            if dominates and strictly:
                dom1.add(a)

        for a in range(cols):
            dominates = True
            strictly = False
            for b in range(cols):
                if a == b:
                    continue
                for i in range(rows):
                    if self.payoffs2[i, a] < self.payoffs2[i, b]:
                        dominates = False
                        break
                    if self.payoffs2[i, a] > self.payoffs2[i, b]:
                        strictly = True
                if not dominates:
                    break
            if dominates and strictly:
                dom2.add(a)

        return {"A": dom1, "B": dom2}

    def table(
        self,
        ax: Optional[plt.Axes] = None,
        show_solution: bool = True,
        player_names: Sequence[str] = ("Player A", "Player B"),
        action_names: Sequence[Sequence[str]] = (("action 0", "action 1"), ("action 0", "action 1")),
    ) -> plt.Axes:
        """Plot a 2x2 payoff table.

        Parameters
        ----------
        ax : matplotlib.axes.Axes, optional
            Axis on which to draw. If ``None``, uses :func:`matplotlib.pyplot.gca`.
        show_solution : bool, default ``True``
            Highlight best responses and Nash equilibria when ``True``.
        player_names : sequence of str, optional
            Names for the row and column players.
        action_names : sequence of sequence of str, optional
            ``action_names[0]`` are actions for player A and ``action_names[1]``
            for player B.

        Returns
        -------
        matplotlib.axes.Axes
            The axis containing the table.

        Notes
        -----
        Currently only works for 2x2 games.
        """

        if self.shape != (2, 2):
            raise ValueError("table() only implemented for 2x2 games")

        if ax is None:
            ax = plt.gca()

        for i in range(2):
            for j in range(2):
                br = self.best_response((i, j))
                a_is_br = br[0] == i
                b_is_br = br[1] == j

                location = (j, -i)
                rec = plt.Rectangle(
                    location,
                    width=-1,
                    height=-1,
                    facecolor="white",
                    edgecolor="black",
                    linewidth=2,
                )
                ax.add_artist(rec)

                p1, p2 = self.payoffs1[i, j], self.payoffs2[i, j]
                s1, s2 = str(p1), str(p2)
                bbox = None
                if show_solution:
                    if a_is_br:
                        s1 = r"\underline{" + s1 + r"}"
                    if b_is_br:
                        s2 = r"\underline{" + s2 + r"}"
                    if a_is_br and b_is_br:
                        bbox = dict(
                            facecolor="lightyellow",
                            edgecolor="black",
                            alpha=0.85,
                        )

                ax.text(
                    j - 0.5,
                    -i - 0.5,
                    f"{s1}, {s2}",
                    va="center",
                    ha="center",
                    size=12,
                    bbox=bbox,
                )

        ax.set_aspect("equal")
        ax.set_ylim(-2.05, 0.05)
        ax.set_xlim(-1.05, 1.05)

        ax.text(
            -0.08,
            0.5,
            player_names[0],
            rotation=90,
            transform=ax.transAxes,
            ha="right",
            va="center",
            size=12,
        )

        ax.text(
            0,
            0.25,
            action_names[0][1],
            rotation=90,
            transform=ax.transAxes,
            ha="right",
            va="center",
            size=10,
        )

        ax.text(
            0,
            0.75,
            action_names[0][0],
            rotation=90,
            transform=ax.transAxes,
            ha="right",
            va="center",
            size=10,
        )

        ax.text(
            0.5,
            1.08,
            player_names[1],
            rotation=0,
            transform=ax.transAxes,
            ha="center",
            va="bottom",
            size=12,
        )

        ax.text(
            0.75,
            1,
            action_names[1][1],
            rotation=0,
            transform=ax.transAxes,
            ha="center",
            va="bottom",
            size=10,
        )

        ax.text(
            0.25,
            1,
            action_names[1][0],
            rotation=0,
            transform=ax.transAxes,
            ha="center",
            va="bottom",
            size=10,
        )

        ax.axis("off")

        return ax


# Backwards compatibility
NormalFormGame = Game


def prisoners_dilemma() -> Game:
    """Return the classic Prisoner's Dilemma game."""

    p1 = [[3, 0], [5, 1]]
    p2 = [[3, 5], [0, 1]]
    return Game(p1, p2)


def matching_pennies() -> Game:
    """Return the Matching Pennies game."""

    p1 = [[1, -1], [-1, 1]]
    p2 = [[-1, 1], [1, -1]]
    return Game(p1, p2)


def stag_hunt() -> Game:
    """Return the Stag Hunt coordination game."""

    p1 = [[2, 0], [1, 1]]
    p2 = [[2, 1], [0, 1]]
    return Game(p1, p2)


def battle_of_the_sexes() -> Game:
    """Return the Battle of the Sexes coordination game."""

    p1 = [[2, 0], [0, 1]]
    p2 = [[1, 0], [0, 2]]
    return Game(p1, p2)


def pure_coordination() -> Game:
    """Return a pure coordination game with two equilibria."""

    p1 = [[1, 0], [0, 1]]
    p2 = [[1, 0], [0, 1]]
    return Game(p1, p2)


def chicken() -> Game:
    """Return the classic Chicken (or Hawk-Dove) game."""

    p1 = [[3, 1], [4, 0]]
    p2 = [[3, 4], [1, 0]]
    return Game(p1, p2)
