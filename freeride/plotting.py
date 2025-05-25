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


def finalize_axes(ax: Optional[plt.Axes] = None) -> plt.Axes:
    """Autoscale and ensure the origin is visible.

    This convenience wraps ``relim`` and ``autoscale_view`` and then
    adjusts the limits so that ``(0, 0)`` always falls within the view.

    Parameters
    ----------
    ax : matplotlib.axes.Axes, optional
        Axis to update. If omitted, the current axes are used.

    Returns
    -------
    matplotlib.axes.Axes
        The updated axes instance.
    """
    if ax is None:
        ax = plt.gca()

    ax.relim()
    ax.autoscale_view()

    xmin, xmax = ax.get_xlim()
    ymin, ymax = ax.get_ylim()

    if xmin > 0:
        xmin = 0
    if xmax < 0:
        xmax = 0
    if ymin > 0:
        ymin = 0
    if ymax < 0:
        ymax = 0

    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)

    return ax
