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

Battle of the Sexes Example
---------------------------

``Game`` comes with constructors for common games.  The ``battle_of_the_sexes``
method returns the classic coordination game.  The table below uses the default
``usetex`` setting (``False``) so that best responses are highlighted with
colored boxes.  The actions are labelled *Opera* and *Boxing Match* with Anna
and Boris as the players.  Boris prefers boxing.

.. code-block:: python

    import matplotlib.pyplot as plt
    from freeride.games import Game

    game = Game.battle_of_the_sexes()
    ax = game.table(
        player_names=["Anna", "Boris"],
        action_names=(
            ("Opera", "Boxing Match"),
            ("Opera", "Boxing Match"),
        ),
    )
    plt.savefig("battle_of_the_sexes.svg", transparent=True)

.. image:: battle_of_the_sexes.svg
   :align: center
   :alt: Battle of the Sexes payoff table
