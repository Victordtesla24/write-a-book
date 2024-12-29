"""Utility functions and classes."""

import json
from datetime import datetime
from typing import Any


class DateTimeEncoder(json.JSONEncoder):
    """JSON encoder that handles datetime objects."""

    def default(self, obj: Any) -> Any:
        """Convert datetime objects to ISO format strings.

        Args:
            obj: Object to convert

        Returns:
            Converted object
        """
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)
