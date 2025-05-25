"""Unit tests for :mod:`freeride.plotting`."""

import unittest

import matplotlib

# Use a non-interactive backend so tests can run without a display.
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np

from freeride.plotting import ALPHA, AREA_FILLS, textbook_axes, update_axes_limits


class TestPlotting(unittest.TestCase):
    """Tests for the plotting utilities."""

    def test_area_fills_values(self):
        """``AREA_FILLS`` should be computed using ``ALPHA`` and the color cycle."""

        expected = [
            np.add(
                np.multiply(ALPHA, np.array(mcolors.to_rgb(f"C{i}"))),
                np.multiply(1 - ALPHA, np.ones(3)),
            ).tolist()
            for i in range(8)
        ]
        self.assertTrue(np.allclose(AREA_FILLS, expected))

    def test_textbook_axes_properties(self):
        """``textbook_axes`` should position spines at the origin and hide others."""

        fig, ax = plt.subplots()
        result = textbook_axes(ax)

        self.assertIs(result, ax)
        self.assertEqual(ax.spines["left"].get_position(), "zero")
        self.assertEqual(ax.spines["bottom"].get_position(), "zero")
        self.assertFalse(ax.spines["top"].get_visible())
        self.assertFalse(ax.spines["right"].get_visible())

    def test_textbook_axes_uses_current_axes(self):
        """When no axis is supplied, ``textbook_axes`` should use the current one."""

        fig, ax = plt.subplots()
        plt.sca(ax)
        result = textbook_axes()

        self.assertIs(result, ax)

    def test_update_axes_limits_includes_origin(self):
        fig, ax = plt.subplots()
        ax.plot([1, 2], [3, 4])
        ax.set_xlim(1, 2)
        ax.set_ylim(3, 4)

        result = update_axes_limits(ax)

        self.assertIs(result, ax)
        x0, x1 = ax.get_xlim()
        y0, y1 = ax.get_ylim()
        self.assertLessEqual(x0, 0)
        self.assertGreaterEqual(x1, 0)
        self.assertLessEqual(y0, 0)
        self.assertGreaterEqual(y1, 0)

    def test_update_axes_limits_uses_current_axes(self):
        fig, ax = plt.subplots()
        plt.sca(ax)
        ax.plot([0, 1], [0, 1])
        result = update_axes_limits()

        self.assertIs(result, ax)

