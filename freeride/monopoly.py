"""Monopoly utilities."""

from __future__ import annotations

import numpy as np

from .curves import Demand
from .costs import Cost
from .revenue import MarginalRevenue


class Monopoly:  # pylint: disable=invalid-name,too-few-public-methods
    """Simple monopoly model given a demand curve and a total cost function."""

    def __init__(self, demand: Demand, total_cost: Cost):
        self.demand = demand
        self.total_cost = total_cost
        self._mc = total_cost.marginal_cost()
        self._mr = MarginalRevenue.from_demand(demand)

        self.q = 0.0
        self.p = 0.0
        self.profit = 0.0

        self._solve()

    def _solve(self):
        candidates = self._candidate_quantities()

        if not candidates:
            self._set_zero_output()
            return

        best_q, best_profit = self._best_candidate(candidates)
        self._set_output(best_q, best_profit)

    def _candidate_quantities(self):
        return (
            self._interior_candidate_quantities()
            + self._boundary_candidate_quantities()
        )

    def _interior_candidate_quantities(self):
        candidates = []

        for mr_piece in self._mr_pieces():
            poly = np.polynomial.Polynomial(self._mc_minus_mr_coefficients(mr_piece))
            for root in poly.roots():
                if not np.isreal(root):
                    continue

                q = float(np.real(root))
                if q > 0 and self._quantity_in_piece_domain(q, mr_piece):
                    candidates.append(q)

        return candidates

    def _boundary_candidate_quantities(self):
        candidates = []

        for q_boundary in self._mr_boundary_points():
            if q_boundary <= 0:
                continue

            mr_left = self._mr_limit_ending_at(q_boundary)
            mr_right = self._mr_limit_starting_at(q_boundary)
            if self._mc_passes_through_mr_gap(q_boundary, mr_left, mr_right):
                candidates.append(q_boundary)

        return candidates

    def _mr_pieces(self):
        return [piece for piece in self._mr.pieces if piece]

    def _mc_minus_mr_coefficients(self, mr_piece):
        mc_coef = list(self._mc.coef)
        if len(mc_coef) < 2:
            mc_coef += [0] * (2 - len(mc_coef))

        diff = mc_coef.copy()
        diff[0] -= mr_piece.intercept
        diff[1] -= mr_piece.slope
        return diff

    def _quantity_in_piece_domain(self, q, piece):
        dom = self._piece_domain(piece)
        return not dom or min(dom) <= q < max(dom)

    def _mr_boundary_points(self):
        boundary_points = set()
        for piece in self._mr.pieces:
            dom = self._piece_domain(piece) if piece else None
            if dom:
                boundary_points.add(max(dom))
        return boundary_points

    def _mr_limit_ending_at(self, q_boundary):
        for piece in self._mr.pieces:
            dom = self._piece_domain(piece) if piece else None
            if dom and max(dom) == q_boundary:
                return piece(q_boundary)
        return None

    def _mr_limit_starting_at(self, q_boundary):
        for piece in self._mr.pieces:
            dom = self._piece_domain(piece) if piece else None
            if dom and min(dom) == q_boundary:
                return piece(q_boundary)
        return None

    @staticmethod
    def _piece_domain(piece):
        return piece._domain  # pylint: disable=protected-access

    def _mc_passes_through_mr_gap(self, q_boundary, mr_left, mr_right):
        if mr_left is None or mr_right is None or mr_left == mr_right:
            return False

        mc_val = self._mc(q_boundary)
        return (mr_left >= mc_val >= mr_right) or (mr_left <= mc_val <= mr_right)

    def _best_candidate(self, candidates):
        best_q = None
        best_profit = -np.inf
        for q in candidates:
            profit = self._profit_at(q)
            if profit > best_profit:
                best_profit = profit
                best_q = q
        return best_q, best_profit

    def _profit_at(self, q):
        return self.demand.p(q) * q - self.total_cost.cost(q)

    def _set_output(self, q, profit):
        self.q = q
        self.p = self.demand.p(q)
        self.profit = profit

    def _set_zero_output(self):
        self.q = 0.0
        self.p = self.demand.p(0)
        self.profit = -self.total_cost.cost(0)

    def __repr__(self) -> str:
        """Return a concise text summary of the monopoly outcome."""
        return f"Monopoly: Q = {self.q:g}, P = {self.p:g}, Profit = {self.profit:g}"

    def _repr_latex_(self) -> str:
        """Return a LaTeX summary for notebook display."""
        return f"$Q^* = {self.q:g},\\ P^* = {self.p:g},\\ \\Pi = {self.profit:g}$"
