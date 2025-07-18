"""Expose the package version and core FreeRide classes."""

# FreeRide
__version__ = '0.1.1'

from .exceptions import FreeRideError, FormulaParseError
from .games import (
    Game,
    NormalFormGame,
)
from .monopoly import Monopoly
from .curves import Demand, Supply
from .equilibrium import Equilibrium, Market

__all__ = [
    "FreeRideError",
    "FormulaParseError",
    "Game",
    "Monopoly",
    "Demand",
    "Supply",
    "Equilibrium",
    "Market",
]
