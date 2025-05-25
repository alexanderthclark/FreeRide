from typing import Optional


class FreeRideError(Exception):
    """Base class for all FreeRide exceptions."""

    def __init__(self, message: Optional[str] = None) -> None:
        if message is None:
            message = "An unspecified FreeRide error occurred."
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:  # pragma: no cover - simple return
        return self.message

    def __repr__(self) -> str:  # pragma: no cover - simple return
        return f"{self.__class__.__name__}('{self.message}')"


class FormulaParseError(FreeRideError):
    """Error raised when parsing a formula string fails."""


class PPFError(FreeRideError):
    """Error raised for invalid production possibility frontiers."""


class PerfectSegmentError(FreeRideError):
    """Raised when perfectly elastic or inelastic segments are unsupported."""


