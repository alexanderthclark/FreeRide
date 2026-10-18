"""Plotting utilities."""

from typing import Optional

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np

ALPHA = 0.5
AREA_FILLS = [
    np.add(
        np.multiply(ALPHA, np.array(mcolors.to_rgb(f"C{i}"))),
        np.multiply(1 - ALPHA, np.ones(3)),
    ).tolist()
    for i in range(0, 8)
]

# Keep market curves and their corresponding welfare areas recognizable together.
DEMAND_COLOR = "#b4473f"
SUPPLY_COLOR = "#287aa7"
CONSUMER_FILL = "#f3d6d2"
PRODUCER_FILL = "#d1e5f0"
REVENUE_FILL = "#e9dfbd"
DWL_FILL = "#d98d81"


def _visible_curve_pieces(curve, q_max, p_max):
    """Yield finite line segments within a market diagram's economic domain."""
    for piece in curve.pieces:
        if piece is None:
            continue
        lo, hi = sorted(piece._domain)
        lo, hi = max(0, lo), min(q_max, hi)
        if not np.isfinite(piece.intercept) or not np.isfinite(piece.slope):
            continue
        if piece.slope:
            price_bounds = sorted((
                -piece.intercept / piece.slope,
                (p_max - piece.intercept) / piece.slope,
            ))
            lo, hi = max(lo, price_bounds[0]), min(hi, price_bounds[1])
        elif not 0 <= piece.intercept <= p_max:
            continue
        if hi > lo:
            yield np.array([lo, hi]), np.array([piece(lo), piece(hi)])


def textbook_axes(ax: Optional[plt.Axes] = None) -> plt.Axes:
    """
    Creates textbook-style axes.

    This function adjusts the properties of the given matplotlib axes object to create
    textbook-style axes where the left and bottom spines are positioned at the origin,
    and the top and right spines are removed.

    Parameters
    ----------
        ax (matplotlib.axes._axes.Axes, optional): The matplotlib axis to modify.
            If not provided, the current axes (`plt.gca()`) will be used.

    Returns
    ----------
        The modified axes object.

    Example
    --------
        To create textbook-style axes on the current plot:

        >>> import matplotlib.pyplot as plt
        >>> plt.plot([0,1], [-1,0])
        >>> textbook_axes()
    """
    if ax is None:
        ax = plt.gca()

    ax.spines["left"].set_position("zero")
    ax.spines["bottom"].set_position("zero")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    return ax


def update_axes_limits(ax: Optional[plt.Axes] = None) -> plt.Axes:
    """Recalculate limits and ensure the origin is visible."""
    if ax is None:
        ax = plt.gca()
    ax.relim()
    ax.autoscale_view()
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    ax.set_xlim(min(x0, 0), max(x1, 0))
    ax.set_ylim(min(y0, 0), max(y1, 0))
    return ax

