# FreeRide
__version__ = '0.0.7'

from .exceptions import FreeRideError, FormulaParseError
from .games import (
    Game,
    NormalFormGame,
    prisoners_dilemma,
    matching_pennies,
    stag_hunt,
    battle_of_the_sexes,
    pure_coordination,
    chicken,
)

__all__ = [
    "FreeRideError",
    "FormulaParseError",
    "Game",
    "NormalFormGame",
    "prisoners_dilemma",
    "matching_pennies",
    "stag_hunt",
    "battle_of_the_sexes",
    "pure_coordination",
    "chicken",
]
