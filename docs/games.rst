Games
=====

.. automodule:: freeride.games
    :members:
    :undoc-members:
    :show-inheritance:

Highlighting Options
--------------------

``Game.table`` accepts a ``usetex`` argument. When set to ``True`` the
underlying text is rendered with LaTeX and best responses are underlined.  When
``False`` (the default), best responses are indicated with colored boxes and no
raw ``\underline`` appears in the output.

Example::

    import matplotlib.pyplot as plt
    from freeride.games import Game

    p1 = [[3, 0], [5, 1]]
    p2 = [[3, 5], [0, 1]]
    g = Game(p1, p2)
    ax = g.table(usetex=False)
    plt.close(ax.figure)
