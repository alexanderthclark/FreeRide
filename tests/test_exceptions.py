import pytest
from freeride.exceptions import FreeRideError, FormulaParseError


def test_base_error_defaults():
    err = FreeRideError()
    assert str(err) == "An unspecified FreeRide error occurred."
    assert repr(err) == "FreeRideError('An unspecified FreeRide error occurred.')"


def test_formula_parse_error_defaults():
    err = FormulaParseError()
    assert str(err) == "Unable to parse formula string."
    assert repr(err) == "FormulaParseError('Unable to parse formula string.')"


def test_custom_message():
    err = FormulaParseError("bad input")
    assert str(err) == "bad input"
    assert repr(err) == "FormulaParseError('bad input')"

