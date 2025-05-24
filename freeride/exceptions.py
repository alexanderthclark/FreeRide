class FreeRideError(Exception):
    """Base class for all FreeRide exceptions."""


class FormulaParseError(FreeRideError):
    """Error raised when parsing a formula string fails."""

