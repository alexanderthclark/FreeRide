"""Monopoly utilities."""

from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt

from .curves import Demand
from .costs import Cost
from .revenue import MarginalRevenue
from .plotting import update_axes_limits


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

    def __repr__(self):
        """Text representation for terminal/console."""
        return f"Monopoly: Q = {self.q:g}, P = {self.p:g}, Profit = {self.profit:g}"
    
    def plot(self, ax=None, show_profit=True):
        """
        Plot the monopoly equilibrium with demand, MR, and MC curves.
        
        Parameters
        ----------
        ax : matplotlib.axes.Axes, optional
            The axes on which to plot. If None, current axes or new figure.
        show_profit : bool, optional
            Whether to shade the profit area. Default is True.
            
        Returns
        -------
        matplotlib.axes.Axes
            The axes object containing the plot.
        """
        if ax is None:
            ax = plt.gca()
        
        # Determine plotting range
        q_int = self.demand.q_intercept if hasattr(self.demand, 'q_intercept') else 10
        max_q = max(q_int, self.q * 2)
        
        # Plot curves
        self.demand.plot(ax=ax, max_q=max_q, label=False)
        self._mr.plot(ax=ax, max_q=max_q, label=False, color='blue')
        self._mc.plot(ax=ax, max_q=max_q, label=False, color='red')
        
        # Add custom labels
        ax.text(max_q * 0.9, self.demand.p(max_q * 0.9), 'D', 
                va='bottom', ha='center', fontsize=12)
        ax.text(max_q * 0.9, self._mr.p(max_q * 0.9) if max_q * 0.9 <= self._mr.q_intercept else 0, 
                'MR', va='top', ha='center', fontsize=12, color='blue')
        ax.text(max_q * 0.9, self._mc(max_q * 0.9), 'MC', 
                va='bottom', ha='center', fontsize=12, color='red')
        
        # Plot equilibrium point
        ax.plot([self.q], [self.p], 'ko', markersize=8)
        
        # Dotted lines to axes
        ax.plot([0, self.q], [self.p, self.p], 'k--', alpha=0.5, linewidth=0.8)
        ax.plot([self.q, self.q], [0, self.p], 'k--', alpha=0.5, linewidth=0.8)
        
        # Shade profit area if requested
        if show_profit and self.profit > 0:
            atc_at_q = self.total_cost.cost(self.q) / self.q if self.q > 0 else 0
            ax.fill_between([0, self.q], atc_at_q, self.p, 
                          alpha=0.3, color='green', label='Profit')
        
        # Labels
        ax.set_xlabel('Quantity')
        ax.set_ylabel('Price')
        ax.set_title('Monopoly Equilibrium')
        
        update_axes_limits(ax)
        
        return ax
    
    @property
    def markup(self):
        """
        Calculate the monopoly markup (Lerner index).
        
        Returns
        -------
        float
            The markup ratio (P - MC) / P
        """
        if self.p == 0:
            return 0
        mc_at_q = self._mc(self.q)
        return (self.p - mc_at_q) / self.p
    
    @property
    def lerner_index(self):
        """
        The Lerner index of market power (same as markup).
        
        Returns
        -------
        float
            The Lerner index (P - MC) / P
        """
        return self.markup
    
    @property
    def consumer_surplus(self):
        """
        Calculate consumer surplus under monopoly.
        
        Returns
        -------
        float
            The consumer surplus
        """
        return self.demand.consumer_surplus(self.p, self.q)
    
    @property
    def producer_surplus(self):
        """
        Calculate producer surplus under monopoly.
        
        Returns
        -------
        float
            The producer surplus (same as profit for monopoly)
        """
        # For a monopolist, producer surplus equals profit
        # since they capture all surplus above their costs
        return self.profit
    
    @property
    def deadweight_loss(self):
        """
        Calculate deadweight loss compared to perfect competition.
        
        Returns
        -------
        float
            The deadweight loss from monopoly pricing
        """
        # Find competitive equilibrium where P = MC
        # This requires solving demand.p(q) = mc(q)
        # For now, we'll use a numerical approach
        from scipy.optimize import fsolve
        
        def excess_demand(q):
            return self.demand.p(q) - self._mc(q)
        
        # Initial guess near monopoly quantity
        q_competitive = fsolve(excess_demand, self.q * 2)[0]
        p_competitive = self.demand.p(q_competitive)
        
        # DWL is the triangle between monopoly and competitive quantities
        dwl = 0
        if q_competitive > self.q:
            # Integrate (P - MC) from q_monopoly to q_competitive
            q_range = np.linspace(self.q, q_competitive, 100)
            for i in range(len(q_range) - 1):
                q_mid = (q_range[i] + q_range[i+1]) / 2
                height = self.demand.p(q_mid) - self._mc(q_mid)
                width = q_range[i+1] - q_range[i]
                dwl += height * width
        
        return dwl
