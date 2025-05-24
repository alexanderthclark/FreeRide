"""Game theory utilities."""

import numpy as np
from typing import List, Tuple

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


# Backwards compatibility
NormalFormGame = Game
