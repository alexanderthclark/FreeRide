"""Game theory utilities."""

import numpy as np
import matplotlib.pyplot as plt
import random
from typing import List, Tuple, Optional, Sequence


def _convex_hull(points: np.ndarray) -> np.ndarray:
    """Return points on the convex hull in counter-clockwise order."""
    pts = sorted(set(map(tuple, points)))
    if len(pts) <= 1:
        return np.asarray(pts)

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower = []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)

    upper = []
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)

    hull = lower[:-1] + upper[:-1]
    return np.asarray(hull)

class Game:
    """Simple two-player game.

    Parameters
    ----------
    payoffs1 : array-like
        Payoff matrix for player 1. Rows correspond to player 1 actions and
        columns correspond to player 2 actions.
    payoffs2 : array-like
        Payoff matrix for player 2 with the same shape as ``payoffs1``.
    player_names : sequence of str, optional
        Names for the row and column players. If omitted the row player name is
        randomly chosen from ``{"Anna", "Alice"}`` and the column player name
        from ``{"Boris", "Bob"}``.
    """

    def __init__(
        self,
        payoffs1,
        payoffs2,
        *,
        player_names: Optional[Sequence[str]] = None,
        action_names: Sequence[Sequence[str]] = (
            ("action 0", "action 1"),
            ("action 0", "action 1"),
        ),
    ):
        self.payoffs1 = np.asarray(payoffs1, dtype=float)
        self.payoffs2 = np.asarray(payoffs2, dtype=float)
        if player_names is None:
            player_names = (
                random.choice(["Anna", "Alice"]),
                random.choice(["Boris", "Bob"]),
            )
        self.player_names = tuple(player_names)
        self.action_names = (
            tuple(action_names[0]),
            tuple(action_names[1]),
        )

        if self.payoffs1.shape != self.payoffs2.shape:
            raise ValueError("Payoff matrices must have the same shape")
        if self.payoffs1.ndim != 2:
            raise ValueError("Payoff matrices must be 2-dimensional")

    @property
    def shape(self) -> Tuple[int, int]:
        return self.payoffs1.shape

    def __repr__(self) -> str:
        """Return a short ASCII summary of the game."""

        p1, p2 = self.player_names
        rows, cols = self.shape

        row_actions = list(self.action_names[0])[:rows]
        col_actions = list(self.action_names[1])[:cols]

        row_width = max([len(r) for r in row_actions] + [0]) + 2

        lines = [f"{p1} \\ {p2}"]
        header = " " * row_width + " ".join(f"{n:>12}" for n in col_actions)
        lines.append(header)

        for i, rname in enumerate(row_actions):
            cells = [
                f"({self.payoffs1[i, j]:g}, {self.payoffs2[i, j]:g})"
                for j in range(cols)
            ]
            line = f"{rname:>{row_width}}" + " ".join(f"{c:>12}" for c in cells)
            lines.append(line)

        return "\n".join(lines)

    def best_response(self, profile: Tuple[int, int]) -> List[int]:
        """Return a best response profile to ``profile``.

        Parameters
        ----------
        profile : tuple of int
            Current actions ``(i, j)`` for players A and B.
        """
        i, j = profile
        br_i = i
        best_payoff_i = self.payoffs1[i, j]
        for alt in range(self.shape[0]):
            payoff = self.payoffs1[alt, j]
            if payoff > best_payoff_i:
                best_payoff_i = payoff
                br_i = alt

        br_j = j
        best_payoff_j = self.payoffs2[i, j]
        for alt in range(self.shape[1]):
            payoff = self.payoffs2[i, alt]
            if payoff > best_payoff_j:
                best_payoff_j = payoff
                br_j = alt

        return [br_i, br_j]

    def best_responses(self) -> Tuple[List[List[int]], List[List[int]]]:
        """Return best responses for each pure strategy profile."""
        rows, cols = self.shape
        br1 = []
        br2 = []
        for j in range(cols):
            col = self.payoffs1[:, j]
            max_val = col.max()
            br1.append([i for i in range(rows) if col[i] == max_val])
        for i in range(rows):
            row = self.payoffs2[i, :]
            max_val = row.max()
            br2.append([j for j in range(cols) if row[j] == max_val])
        return br1, br2

    def nash_equilibria(self) -> List[Tuple[str, str]]:
        """Compute pure strategy Nash equilibria.

        Returns
        -------
        list of tuple of str
            List of Nash equilibria as strategy profiles (action name pairs).
            Each equilibrium is a tuple of (player1_action, player2_action).
            A Nash equilibrium is a strategy profile where no player can
            unilaterally deviate and improve their payoff.
        """
        br1, br2 = self.best_responses()
        eqs = []
        for j, rows in enumerate(br1):
            for i in rows:
                if j in br2[i]:
                    action1 = self.action_names[0][i]
                    action2 = self.action_names[1][j]
                    eqs.append((action1, action2))
        return eqs

    def nash(self) -> List[Tuple[str, str]]:
        """Alias for :meth:`nash_equilibria`."""
        return self.nash_equilibria()

    def mixed_strategy_equilibrium(self) -> Tuple[float, float]:
        """Return mixed strategy equilibrium for 2x2 games."""
        if self.shape != (2, 2):
            raise ValueError("Mixed strategy solver only implemented for 2x2 games")

        a, b = self.payoffs1[0]
        c, d = self.payoffs1[1]
        e, f = self.payoffs2[0]
        g, h = self.payoffs2[1]

        denom_q = a - b - c + d
        denom_p = e - f - g + h
        if denom_q == 0 or denom_p == 0:
            raise ValueError("Game has no mixed strategy equilibrium")

        q = (d - b) / denom_q
        p = (h - g) / denom_p
        return p, q

    def weakly_dominant_strategies(self) -> dict:
        """Return weakly dominant strategies for both players."""

        rows, cols = self.shape
        dom1 = set()
        dom2 = set()

        for a in range(rows):
            dominates = True
            strictly = False
            for b in range(rows):
                if a == b:
                    continue
                for j in range(cols):
                    if self.payoffs1[a, j] < self.payoffs1[b, j]:
                        dominates = False
                        break
                    if self.payoffs1[a, j] > self.payoffs1[b, j]:
                        strictly = True
                if not dominates:
                    break
            if dominates and strictly:
                dom1.add(a)

        for a in range(cols):
            dominates = True
            strictly = False
            for b in range(cols):
                if a == b:
                    continue
                for i in range(rows):
                    if self.payoffs2[i, a] < self.payoffs2[i, b]:
                        dominates = False
                        break
                    if self.payoffs2[i, a] > self.payoffs2[i, b]:
                        strictly = True
                if not dominates:
                    break
            if dominates and strictly:
                dom2.add(a)

        return {"A": dom1, "B": dom2}

    def table(
        self,
        ax: Optional[plt.Axes] = None,
        show_solution: bool = True,
        player_names: Optional[Sequence[str]] = None,
        action_names: Optional[Sequence[Sequence[str]]] = None,
        usetex: bool = False,
    ) -> plt.Axes:
        """Plot a payoff table.

        Parameters
        ----------
        ax : matplotlib.axes.Axes, optional
            Axis on which to draw. If ``None``, uses :func:`matplotlib.pyplot.gca`.
        show_solution : bool, default ``True``
            Highlight best responses and Nash equilibria when ``True``.
        player_names : sequence of str, optional
            Names for the row and column players.  Defaults to the names stored
            on the ``Game`` instance.
        action_names : sequence of sequence of str, optional
            ``action_names[0]`` are actions for player A and ``action_names[1]``
            for player B. Defaults to the names stored on the ``Game`` instance.
        usetex : bool, default ``False``
            Use LaTeX for text rendering and underline best responses when
            ``True``. When ``False``, best responses are highlighted with colored
            boxes.

        Returns
        -------
        matplotlib.axes.Axes
            The axis containing the table.

        Notes
        -----
        Supports arbitrary ``rows \times cols`` games.
        """

        rows, cols = self.shape

        if ax is None:
            ax = plt.gca()

        if player_names is None:
            player_names = self.player_names
        if action_names is None:
            action_names = self.action_names

        prev = plt.rcParams.get("text.usetex", False)
        if usetex:
            plt.rcParams["text.usetex"] = True

        for i in range(rows):
            for j in range(cols):
                br = self.best_response((i, j))
                a_is_br = br[0] == i
                b_is_br = br[1] == j

                location = (j, -i)
                rec = plt.Rectangle(
                    location,
                    width=-1,
                    height=-1,
                    facecolor="white",
                    edgecolor="black",
                    linewidth=2,
                )
                ax.add_artist(rec)

                p1, p2 = self.payoffs1[i, j], self.payoffs2[i, j]
                s1, s2 = str(p1), str(p2)

                cell_bbox = None
                bbox1 = None
                bbox2 = None
                if show_solution:
                    if usetex:
                        if a_is_br:
                            s1 = r"\underline{" + s1 + r"}"
                        if b_is_br:
                            s2 = r"\underline{" + s2 + r"}"
                        if a_is_br and b_is_br:
                            cell_bbox = dict(
                                facecolor="lightyellow",
                                edgecolor="black",
                                alpha=0.85,
                            )
                    else:
                        if a_is_br and b_is_br:
                            cell_bbox = dict(
                                facecolor="lightyellow",
                                edgecolor="black",
                                alpha=0.85,
                            )
                        if a_is_br:
                            bbox1 = dict(facecolor="lightblue", edgecolor="none", alpha=0.5)
                        if b_is_br:
                            bbox2 = dict(facecolor="lightgreen", edgecolor="none", alpha=0.5)

                if cell_bbox is not None and not usetex:
                    patch = plt.Rectangle(
                        location,
                        width=-1,
                        height=-1,
                        **cell_bbox,
                    )
                    ax.add_artist(patch)

                if usetex:
                    text = f"${s1}$, ${s2}$"
                    ax.text(
                        j - 0.5,
                        -i - 0.5,
                        text,
                        va="center",
                        ha="center",
                        size=12,
                        bbox=cell_bbox,
                    )
                else:
                    ax.text(
                        j - 0.55,
                        -i - 0.5,
                        f"{s1},",
                        va="center",
                        ha="right",
                        size=12,
                        bbox=bbox1,
                    )
                    ax.text(
                        j - 0.45,
                        -i - 0.5,
                        s2,
                        va="center",
                        ha="left",
                        size=12,
                        bbox=bbox2,
                    )

        ax.set_aspect("equal")
        ax.set_ylim(-rows - 0.05, 0.05)
        ax.set_xlim(-1.05, cols - 1 + 0.05)

        ax.text(
            -0.08,
            0.5,
            player_names[0],
            rotation=90,
            transform=ax.transAxes,
            ha="right",
            va="center",
            size=12,
        )

        for i in range(rows):
            ax.text(
                0,
                1 - (i + 0.5) / rows,
                action_names[0][i],
                rotation=90,
                transform=ax.transAxes,
                ha="right",
                va="center",
                size=10,
            )

        ax.text(
            0.5,
            1.08,
            player_names[1],
            rotation=0,
            transform=ax.transAxes,
            ha="center",
            va="bottom",
            size=12,
        )

        for j in range(cols):
            ax.text(
                (j + 0.5) / cols,
                1,
                action_names[1][j],
                rotation=0,
                transform=ax.transAxes,
                ha="center",
                va="bottom",
                size=10,
            )

        ax.axis("off")

        # Restore previous TeX setting
        plt.rcParams["text.usetex"] = prev

        return ax

    def plot_payoff_hull(
        self,
        ax: Optional[plt.Axes] = None,
        annotate: bool = False,
    ) -> plt.Axes:
        """Plot the convex hull of payoff pairs for the game."""

        if ax is None:
            ax = plt.gca()

        pts = np.column_stack((self.payoffs1.ravel(), self.payoffs2.ravel()))
        hull = _convex_hull(pts)

        if hull.size > 0:
            closed = np.vstack([hull, hull[0]])
            ax.fill(closed[:, 0], closed[:, 1], color="lightgray", alpha=0.5)
            ax.plot(closed[:, 0], closed[:, 1], color="black", lw=1)

        ax.scatter(pts[:, 0], pts[:, 1], color="C0")

        if annotate:
            rows, cols = self.shape
            for i in range(rows):
                for j in range(cols):
                    label = f"({self.action_names[0][i]}, {self.action_names[1][j]})"
                    ax.text(
                        self.payoffs1[i, j],
                        self.payoffs2[i, j],
                        label,
                        fontsize=8,
                        ha="left",
                        va="bottom",
                    )

        ax.set_xlabel(f"Payoff to {self.player_names[0]}")
        ax.set_ylabel(f"Payoff to {self.player_names[1]}")
        ax.set_title("Payoff Hull")
        ax.set_aspect("equal", adjustable="datalim")

        return ax

    @classmethod
    def prisoners_dilemma(cls) -> "Game":
        """Return the classic Prisoner's Dilemma game."""

        p1 = [[3, 0], [5, 1]]
        p2 = [[3, 5], [0, 1]]
        return cls(
            p1,
            p2,
            action_names=(
                ("Cooperate", "Defect"),
                ("Cooperate", "Defect"),
            ),
        )

    @classmethod
    def matching_pennies(cls) -> "Game":
        """Return the Matching Pennies game."""

        p1 = [[1, -1], [-1, 1]]
        p2 = [[-1, 1], [1, -1]]
        return cls(
            p1,
            p2,
            action_names=(
                ("Heads", "Tails"),
                ("Heads", "Tails"),
            ),
        )

    @classmethod
    def stag_hunt(cls) -> "Game":
        """Return the Stag Hunt coordination game."""

        p1 = [[2, 0], [1, 1]]
        p2 = [[2, 1], [0, 1]]
        return cls(
            p1,
            p2,
            action_names=(
                ("Stag", "Hare"),
                ("Stag", "Hare"),
            ),
        )

    @classmethod
    def battle_of_the_sexes(cls) -> "Game":
        """Return the Battle of the Sexes coordination game."""

        p1 = [[2, 0], [0, 1]]
        p2 = [[1, 0], [0, 2]]
        return cls(
            p1,
            p2,
            player_names=("Anna", "Boris"),
            action_names=(("Opera", "Boxing Match"), ("Opera", "Boxing Match")),
        )

    @classmethod
    def pure_coordination(cls) -> "Game":
        """Return a simple pure coordination game."""

        p1 = [[1, 0], [0, 1]]
        p2 = [[1, 0], [0, 1]]
        return cls(
            p1,
            p2,
            action_names=(
                ("Left", "Right"),
                ("Left", "Right"),
            ),
        )

    @classmethod
    def chicken(cls) -> "Game":
        """Return the classic Chicken (Hawk-Dove) game."""

        p1 = [[3, 1], [4, 0]]
        p2 = [[3, 4], [1, 0]]
        return cls(
            p1,
            p2,
            action_names=(
                ("Straight", "Swerve"),
                ("Straight", "Swerve"),
            ),
        )

    @classmethod
    def rock_paper_scissors(cls) -> "Game":
        """Return the Rock-Paper-Scissors game."""

        p1 = [
            [0, -1, 1],
            [1, 0, -1],
            [-1, 1, 0],
        ]
        p2 = [
            [0, 1, -1],
            [-1, 0, 1],
            [1, -1, 0],
        ]
        return cls(
            p1,
            p2,
            action_names=(
                ("Rock", "Paper", "Scissors"),
                ("Rock", "Paper", "Scissors"),
            ),
        )


# Backwards compatibility
NormalFormGame = Game

