"""Tests for the utils module."""

import json
from datetime import datetime

import pytest

from src.book_editor.core.utils import DateTimeEncoder


def test_datetime_encoder():
    """Test DateTimeEncoder class."""
    now = datetime.now()
    data = {
        "timestamp": now,
        "string": "test",
        "number": 42,
        "list": [1, 2, 3],
        "dict": {"key": "value"},
    }

    # Test encoding with DateTimeEncoder
    encoded = json.dumps(data, cls=DateTimeEncoder)
    decoded = json.loads(encoded)

    # Verify that datetime was converted to ISO format string
    assert decoded["timestamp"] == now.isoformat()

    # Verify that other types remain unchanged
    assert decoded["string"] == "test"
    assert decoded["number"] == 42
    assert decoded["list"] == [1, 2, 3]
    assert decoded["dict"] == {"key": "value"}


def test_datetime_encoder_nested():
    """Test DateTimeEncoder with nested datetime objects."""
    now = datetime.now()
    data = {
        "nested": {
            "timestamp": now,
            "list": [now, "test", 42],
            "dict": {"time": now},
        }
    }

    # Test encoding with DateTimeEncoder
    encoded = json.dumps(data, cls=DateTimeEncoder)
    decoded = json.loads(encoded)

    # Verify that all datetime objects were converted
    assert decoded["nested"]["timestamp"] == now.isoformat()
    assert decoded["nested"]["list"][0] == now.isoformat()
    assert decoded["nested"]["dict"]["time"] == now.isoformat()

    # Verify that other types remain unchanged
    assert decoded["nested"]["list"][1] == "test"
    assert decoded["nested"]["list"][2] == 42


def test_datetime_encoder_unsupported():
    """Test DateTimeEncoder with unsupported types."""
    class UnsupportedType:
        pass

    data = {"unsupported": UnsupportedType()}

    # Test encoding with DateTimeEncoder
    with pytest.raises(TypeError):
        json.dumps(data, cls=DateTimeEncoder) 