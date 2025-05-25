"""Unit tests for :mod:`freeride.plotting`."""

import unittest

import matplotlib

# Use a non-interactive backend so tests can run without a display.
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np

from freeride.plotting import ALPHA, AREA_FILLS, textbook_axes, finalize_axes


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

    def test_finalize_axes_includes_origin(self):
        """``finalize_axes`` should ensure the origin is visible."""

        fig, ax = plt.subplots()
        ax.plot([1, 2], [1, 2])
        finalize_axes(ax)

        self.assertLessEqual(ax.get_xlim()[0], 0)
        self.assertLessEqual(ax.get_ylim()[0], 0)

    def test_finalize_axes_uses_current_axes(self):
        """When no axis is supplied, ``finalize_axes`` should use the current one."""

        fig, ax = plt.subplots()
        plt.sca(ax)
        ax.plot([1, 2], [1, 2])
        result = finalize_axes()

        self.assertIs(result, ax)

