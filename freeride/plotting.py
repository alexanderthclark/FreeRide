'''
Plotting module.
'''
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.colors as mcolors
import numpy as np

C0 = np.array(mcolors.to_rgb('C0'))
ALPHA = 0.5
AREA_FILLS = [np.add(np.multiply(ALPHA, np.array(mcolors.to_rgb(f'C{i}'))), np.multiply(1-ALPHA, np.ones(3))).tolist() for i in range(0, 8)]

def textbook_axes(ax=None):
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
        None

    Example
    --------
        To create textbook-style axes on the current plot:

        >>> import matplotlib.pyplot as plt
        >>> plt.plot([0,1], [-1,0])
        >>> textbook_axes()
    """
    if ax is None:
        ax = plt.gca()

    ax.spines['left'].set_position('zero')
    ax.spines['bottom'].set_position('zero')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)