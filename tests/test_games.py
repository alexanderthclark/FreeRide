import unittest

from freeride.games import Game, NormalFormGame


class TestGame(unittest.TestCase):
    def test_pure_equilibrium(self):
        p1 = [[3, 0], [5, 1]]
        p2 = [[3, 5], [0, 1]]
        game = Game(p1, p2)
        self.assertEqual(game.nash_equilibria(), [(1, 1)])

    def test_mixed_strategy(self):
        p1 = [[1, -1], [-1, 1]]
        p2 = [[-1, 1], [1, -1]]
        game = Game(p1, p2)
        p, q = game.mixed_strategy_equilibrium()
        self.assertAlmostEqual(p, 0.5)
        self.assertAlmostEqual(q, 0.5)

    def test_alias(self):
        self.assertIs(NormalFormGame, Game)

    def test_weakly_dominant(self):
        p1 = [[1, 1], [0, 0]]
        p2 = [[1, 1], [1, 0]]
        game = Game(p1, p2)
        self.assertEqual(game.weakly_dominant_strategies(), {"A": {0}, "B": {0}})


if __name__ == '__main__':
    unittest.main()
