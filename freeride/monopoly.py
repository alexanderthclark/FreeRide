"""Monopoly utilities."""

from __future__ import annotations

import numpy as np

from .curves import Demand
from .costs import Cost
from .revenue import MarginalRevenue


class Monopoly:
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
        candidates = []

        # Find interior solutions where MR = MC
        # For each MR piece, solve MR(q) = MC(q)
        for mr_piece in [p for p in self._mr.pieces if p]:
            mc_coef = list(self._mc.coef)
            if len(mc_coef) < 2:
                mc_coef += [0] * (2 - len(mc_coef))
            diff = mc_coef.copy()
            diff[0] -= mr_piece.intercept
            diff[1] -= mr_piece.slope
            poly = np.polynomial.Polynomial(diff)
            for r in poly.roots():
                if np.isreal(r):
                    q = float(np.real(r))
                    if q <= 0:
                        continue
                    # Check if q is in the domain of this MR piece
                    dom = mr_piece._domain
                    if dom and not (min(dom) <= q < max(dom)):
                        continue
                    candidates.append(q)

        # Check discontinuity points where MC might pass through MR gaps
        # Find boundaries between MR pieces using [a,b) convention
        boundary_points = set()
        for piece in self._mr.pieces:
            if piece and piece._domain:
                # Right boundary of [a,b) is where discontinuities can occur
                boundary_points.add(max(piece._domain))

        for q_boundary in boundary_points:
            if q_boundary <= 0:
                continue

            # Calculate MC at the boundary
            mc_val = self._mc(q_boundary)

            # Find MR left limit (from piece ending at this boundary)
            mr_left = None
            for piece in self._mr.pieces:
                if piece and piece._domain and max(piece._domain) == q_boundary:
                    # This piece ends at the boundary - get left limit
                    mr_left = piece(q_boundary)
                    break

            # Find MR right limit (from piece starting at this boundary)
            mr_right = None
            for piece in self._mr.pieces:
                if piece and piece._domain and min(piece._domain) == q_boundary:
                    # This piece starts at the boundary - get right limit
                    mr_right = piece(q_boundary)
                    break

            # If MC passes through the MR gap, this is profit-maximizing
            if mr_left is not None and mr_right is not None and mr_left != mr_right:
                # Check if MC is between the left and right limits
                if (mr_left >= mc_val >= mr_right) or (mr_left <= mc_val <= mr_right):
                    candidates.append(q_boundary)

        if not candidates:
            self.q = 0.0
            self.p = self.demand.p(0)
            self.profit = -self.total_cost.cost(0)
            return

        best_q = None
        best_profit = -np.inf
        for q in candidates:
            p = self.demand.p(q)
            profit = p * q - self.total_cost.cost(q)
            if profit > best_profit:
                best_profit = profit
                best_q = q

        self.q = best_q
        self.p = self.demand.p(best_q)
        self.profit = best_profit
