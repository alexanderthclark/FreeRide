import unittest

import matplotlib

# Use a non-interactive backend so tests can run without a display.
matplotlib.use("Agg")

import matplotlib.pyplot as plt

from freeride.games import Game, NormalFormGame


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

    def test_no_raw_underline_without_tex(self):
        r"""Ensure ``\underline`` is not used when ``usetex=False``."""

        p1 = [[3, 0], [5, 1]]
        p2 = [[3, 5], [0, 1]]
        game = Game(p1, p2)
        ax = game.table(usetex=False)
        texts = [t.get_text() for t in ax.texts]
        self.assertFalse(any("\\underline" in t for t in texts))

    def test_tex_highlighting(self):
        r"""Best response highlighting works with ``usetex=True``."""

        p1 = [[3, 0], [5, 1]]
        p2 = [[3, 5], [0, 1]]
        game = Game(p1, p2)
        ax = game.table(usetex=True)
        texts = [t.get_text() for t in ax.texts]
        self.assertTrue(any("\\underline" in t for t in texts))

    def test_class_helpers(self):
        """Class helper methods should build the expected games."""

        g = Game.prisoners_dilemma()
        self.assertEqual(g.payoffs1.tolist(), [[3, 0], [5, 1]])
        self.assertEqual(g.payoffs2.tolist(), [[3, 5], [0, 1]])
        self.assertEqual(
            g.action_names,
            (("Cooperate", "Defect"), ("Cooperate", "Defect")),
        )

        mp = Game.matching_pennies()
        self.assertEqual(mp.payoffs1.tolist(), [[1, -1], [-1, 1]])
        self.assertEqual(mp.payoffs2.tolist(), [[-1, 1], [1, -1]])
        self.assertEqual(mp.action_names, (("Heads", "Tails"), ("Heads", "Tails")))

        bos = Game.battle_of_the_sexes()
        self.assertEqual(bos.payoffs1.tolist(), [[2, 0], [0, 1]])
        self.assertEqual(bos.payoffs2.tolist(), [[1, 0], [0, 2]])
        self.assertEqual(bos.player_names, ("Anna", "Boris"))
        self.assertEqual(
            bos.action_names,
            (("Opera", "Boxing Match"), ("Opera", "Boxing Match")),
        )

        sh = Game.stag_hunt()
        self.assertEqual(sh.payoffs1.tolist(), [[2, 0], [1, 1]])
        self.assertEqual(sh.payoffs2.tolist(), [[2, 1], [0, 1]])
        self.assertEqual(sh.action_names, (("Stag", "Hare"), ("Stag", "Hare")))

        pc = Game.pure_coordination()
        self.assertEqual(pc.payoffs1.tolist(), [[1, 0], [0, 1]])
        self.assertEqual(pc.payoffs2.tolist(), [[1, 0], [0, 1]])
        self.assertEqual(pc.action_names, (("Left", "Right"), ("Left", "Right")))

        ch = Game.chicken()
        self.assertEqual(ch.payoffs1.tolist(), [[3, 1], [4, 0]])
        self.assertEqual(ch.payoffs2.tolist(), [[3, 4], [1, 0]])
        self.assertEqual(
            ch.action_names,
            (("Straight", "Swerve"), ("Straight", "Swerve")),
        )


if __name__ == '__main__':
    unittest.main()
