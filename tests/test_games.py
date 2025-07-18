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
        # Nash equilibrium is (Defect, Defect) - both players choose action 1
        self.assertEqual(game.nash_equilibria(), [('action 1', 'action 1')])

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
        # Two equilibria: (Stag, Stag) and (Hare, Hare)
        self.assertEqual(set(game.nash_equilibria()), {('action 0', 'action 0'), ('action 1', 'action 1')})

    def test_battle_of_the_sexes(self):
        p1 = [[2, 0], [0, 1]]
        p2 = [[1, 0], [0, 2]]
        game = Game(p1, p2)
        # Two equilibria: both at Opera or both at Boxing Match
        self.assertEqual(set(game.nash_equilibria()), {('action 0', 'action 0'), ('action 1', 'action 1')})

    def test_pure_coordination(self):
        p1 = [[1, 0], [0, 1]]
        p2 = [[1, 0], [0, 1]]
        game = Game(p1, p2)
        # Two equilibria: both Left or both Right
        self.assertEqual(set(game.nash_equilibria()), {('action 0', 'action 0'), ('action 1', 'action 1')})

    def test_chicken(self):
        p1 = [[3, 1], [4, 0]]
        p2 = [[3, 4], [1, 0]]
        game = Game(p1, p2)
        # Two equilibria: one Swerves, one goes Straight
        self.assertEqual(set(game.nash_equilibria()), {('action 1', 'action 0'), ('action 0', 'action 1')})

    def test_rock_paper_scissors(self):
        """Rock-paper-scissors has no pure Nash equilibria."""

        game = Game.rock_paper_scissors()
        self.assertEqual(
            game.payoffs1.tolist(),
            [[0, -1, 1], [1, 0, -1], [-1, 1, 0]],
        )
        self.assertEqual(
            game.payoffs2.tolist(),
            [[0, 1, -1], [-1, 0, 1], [1, -1, 0]],
        )
        self.assertEqual(game.nash_equilibria(), [])

    def test_alias(self):
        self.assertIs(NormalFormGame, Game)

    def test_weakly_dominant(self):
        p1 = [[1, 1], [0, 0]]
        p2 = [[1, 1], [1, 0]]
        game = Game(p1, p2)
        self.assertEqual(game.weakly_dominant_strategies(), {"A": {0}, "B": {0}})

    def test_repr_includes_player_names(self):
        """Representation should mention both player names."""

        game = Game([[0]], [[0]], player_names=("Alice", "Bob"))
        rep = repr(game)
        self.assertIn("Alice", rep)
        self.assertIn("Bob", rep)

    def test_repr_contains_payoff_table(self):
        """``repr`` should show payoff pairs."""

        g = Game(
            [[1, 2], [3, 4]],
            [[5, 6], [7, 8]],
            player_names=("A", "B"),
            action_names=(("X", "Y"), ("L", "R")),
        )
        rep = repr(g)
        self.assertIn("(1, 5)", rep)
        self.assertIn("(4, 8)", rep)

    def test_table_returns_axes(self):
        """The ``table`` method should return a Matplotlib ``Axes`` object."""

        p1 = [[3, 0], [5, 1]]
        p2 = [[3, 5], [0, 1]]
        game = Game(p1, p2)
        ax = game.table()
        self.assertIsInstance(ax, plt.Axes)

    def test_table_returns_axes_non_square(self):
        """``table`` should support games larger than 2x2."""

        p1 = [
            [0, 1, 2],
            [3, 4, 5],
            [6, 7, 8],
        ]
        p2 = [
            [0, 0, 0],
            [1, 1, 1],
            [2, 2, 2],
        ]
        game = Game(
            p1,
            p2,
            action_names=(
                ("r0", "r1", "r2"),
                ("c0", "c1", "c2"),
            ),
        )
        ax = game.table()
        self.assertIsInstance(ax, plt.Axes)

    def test_payoff_hull_returns_axes(self):
        """``plot_payoff_hull`` should return a Matplotlib ``Axes`` object."""

        p1 = [[3, 0], [5, 1]]
        p2 = [[3, 5], [0, 1]]
        game = Game(p1, p2)
        ax = game.plot_payoff_hull()
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

    def test_individual_highlighting(self):
        """Only the payoff of the player with a best response is highlighted."""

        p1 = [[3, 0], [5, 1]]
        p2 = [[3, 5], [0, 1]]
        game = Game(p1, p2)
        ax = game.table(usetex=False)

        highlighted_5 = False
        zero_highlighted = False
        for t in ax.texts:
            patch = t.get_bbox_patch()
            if t.get_text().startswith("5") and patch is not None:
                highlighted_5 = True
            if t.get_text() == "0.0" and patch is not None:
                zero_highlighted = True

        self.assertTrue(highlighted_5)
        self.assertFalse(zero_highlighted)

    def test_class_helpers(self):
        """Class helper methods should build the expected games."""

        g = Game.prisoners_dilemma()
        self.assertEqual(g.payoffs1.tolist(), [[3, 0], [5, 1]])
        self.assertEqual(g.payoffs2.tolist(), [[3, 5], [0, 1]])
        self.assertEqual(
            g.action_names,
            (("Cooperate", "Defect"), ("Cooperate", "Defect")),
        )
        # Test that nash equilibrium returns action names for predefined games
        self.assertEqual(g.nash_equilibria(), [('Defect', 'Defect')])

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
        # Test nash equilibrium with proper action names
        self.assertEqual(set(bos.nash_equilibria()), {('Opera', 'Opera'), ('Boxing Match', 'Boxing Match')})

        sh = Game.stag_hunt()
        self.assertEqual(sh.payoffs1.tolist(), [[2, 0], [1, 1]])
        self.assertEqual(sh.payoffs2.tolist(), [[2, 1], [0, 1]])
        self.assertEqual(sh.action_names, (("Stag", "Hare"), ("Stag", "Hare")))
        # Test nash equilibrium returns proper action names
        self.assertEqual(set(sh.nash_equilibria()), {('Stag', 'Stag'), ('Hare', 'Hare')})

        pc = Game.pure_coordination()
        self.assertEqual(pc.payoffs1.tolist(), [[1, 0], [0, 1]])
        self.assertEqual(pc.payoffs2.tolist(), [[1, 0], [0, 1]])
        self.assertEqual(pc.action_names, (("Left", "Right"), ("Left", "Right")))
        # Test nash equilibrium returns proper action names
        self.assertEqual(set(pc.nash_equilibria()), {('Left', 'Left'), ('Right', 'Right')})

        ch = Game.chicken()
        self.assertEqual(ch.payoffs1.tolist(), [[3, 1], [4, 0]])
        self.assertEqual(ch.payoffs2.tolist(), [[3, 4], [1, 0]])
        self.assertEqual(
            ch.action_names,
            (("Straight", "Swerve"), ("Straight", "Swerve")),
        )
        # Test nash equilibrium returns proper action names
        self.assertEqual(set(ch.nash_equilibria()), {('Swerve', 'Straight'), ('Straight', 'Swerve')})

        rps = Game.rock_paper_scissors()
        self.assertEqual(
            rps.payoffs1.tolist(),
            [[0, -1, 1], [1, 0, -1], [-1, 1, 0]],
        )
        self.assertEqual(
            rps.payoffs2.tolist(),
            [[0, 1, -1], [-1, 0, 1], [1, -1, 0]],
        )
        self.assertEqual(
            rps.action_names,
            (("Rock", "Paper", "Scissors"), ("Rock", "Paper", "Scissors")),
        )
