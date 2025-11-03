"""
Custom logging filters.
"""

import logging
import os
from typing import override


class OnlyIfDev(logging.Filter):
    """Filters out all log records unless DEV_LOGGING=true."""

    @override
    def filter(self, record: logging.LogRecord) -> bool:
        """Log record is included only when DEV_LOGGING=true."""
        return os.environ.get("DEV_LOGGING") == "true"
