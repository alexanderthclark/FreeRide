class FreeRideError(Exception):
    """Base class for all FreeRide exceptions."""

    def __init__(self, message: str | None = None) -> None:
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

    def __init__(self, message: str | None = None) -> None:
        if message is None:
            message = "Failed to parse formula."
        super().__init__(message)

    def __str__(self) -> str:  # pragma: no cover - simple return
        return self.message

    def __repr__(self) -> str:  # pragma: no cover - simple return
        return f"{self.__class__.__name__}('{self.message}')"


