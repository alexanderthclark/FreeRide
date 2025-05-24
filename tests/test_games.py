import unittest

import matplotlib

# Use a non-interactive backend so tests can run without a display.
matplotlib.use("Agg")

import matplotlib.pyplot as plt

from freeride.games import (
    Game,
    NormalFormGame,
    prisoners_dilemma,
    matching_pennies,
    stag_hunt,
    battle_of_the_sexes,
    pure_coordination,
    chicken,
)


class TestGame(unittest.TestCase):
    def test_prisoners_dilemma(self):
        p1 = [[3, 0], [5, 1]]
        p2 = [[3, 5], [0, 1]]
        game = Game(p1, p2)
        self.assertEqual(game.nash_equilibria(), [(1, 1)])

    def test_matching_pennies(self):
        p1 = [[1, -1], [-1, 1]]
        p2 = [[-1, 1], [1, -1]]
        game = Game(p1, p2)
        self.assertEqual(game.nash_equilibria(), [])
        p, q = game.mixed_strategy_equilibrium()
        self.assertAlmostEqual(p, 0.5)
        self.assertAlmostEqual(q, 0.5)

    def test_stag_hunt(self):
        p1 = [[2, 0], [1, 1]]
        p2 = [[2, 1], [0, 1]]
        game = Game(p1, p2)
        self.assertEqual(set(game.nash_equilibria()), {(0, 0), (1, 1)})

    def test_battle_of_the_sexes(self):
        p1 = [[2, 0], [0, 1]]
        p2 = [[1, 0], [0, 2]]
        game = Game(p1, p2)
        self.assertEqual(set(game.nash_equilibria()), {(0, 0), (1, 1)})

    def test_pure_coordination(self):
        p1 = [[1, 0], [0, 1]]
        p2 = [[1, 0], [0, 1]]
        game = Game(p1, p2)
        self.assertEqual(set(game.nash_equilibria()), {(0, 0), (1, 1)})

    def test_chicken(self):
        p1 = [[3, 1], [4, 0]]
        p2 = [[3, 4], [1, 0]]
        game = Game(p1, p2)
        self.assertEqual(set(game.nash_equilibria()), {(1, 0), (0, 1)})

    def test_alias(self):
        self.assertIs(NormalFormGame, Game)

    def test_weakly_dominant(self):
        p1 = [[1, 1], [0, 0]]
        p2 = [[1, 1], [1, 0]]
        game = Game(p1, p2)
        self.assertEqual(game.weakly_dominant_strategies(), {"A": {0}, "B": {0}})

    def test_table_returns_axes(self):
        """The ``table`` method should return a Matplotlib ``Axes`` object."""

        p1 = [[3, 0], [5, 1]]
        p2 = [[3, 5], [0, 1]]
        game = Game(p1, p2)
        ax = game.table()
        self.assertIsInstance(ax, plt.Axes)

    def test_helper_functions(self):
        helpers = [
            (prisoners_dilemma, [[3, 0], [5, 1]], [[3, 5], [0, 1]]),
            (matching_pennies, [[1, -1], [-1, 1]], [[-1, 1], [1, -1]]),
            (stag_hunt, [[2, 0], [1, 1]], [[2, 1], [0, 1]]),
            (battle_of_the_sexes, [[2, 0], [0, 1]], [[1, 0], [0, 2]]),
            (pure_coordination, [[1, 0], [0, 1]], [[1, 0], [0, 1]]),
            (chicken, [[3, 1], [4, 0]], [[3, 4], [1, 0]]),
        ]

        for func, p1, p2 in helpers:
            game = func()
            self.assertIsInstance(game, Game)
            self.assertEqual(game.payoffs1.tolist(), p1)
            self.assertEqual(game.payoffs2.tolist(), p2)


if __name__ == '__main__':
    unittest.main()
