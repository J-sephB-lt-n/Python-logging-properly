"""
Logging formatters.
"""

import datetime as dt
import json
import logging
from typing import Any, override

# from https://docs.python.org/3/library/logging.html#logrecord-attributes
_RESERVED_LOG_RECORD_ATTRS = frozenset(
    (
        "args",
        "asctime",
        "created",
        "exc_info",
        "filename",
        "funcName",
        "levelname",
        "levelno",
        "lineno",
        "message",
        "module",
        "msecs",
        "msg",
        "name",
        "pathname",
        "process",
        "processName",
        "relativeCreated",
        "stack_info",
        "thread",
        "threadName",
        "taskName",
    )
)


class JsonLogFormatter(logging.Formatter):
    """A logging formatter that outputs log records as JSON strings.

    Attributes:
        fmt_keys (dict[str, str]): A dictionary mapping output JSON keys to
            `LogRecord` attribute names.
    """

    def __init__(self, *, fmt_keys: dict[str, str] | None = None) -> None:
        """Initializes the JsonLogFormatter.

        Args:
            fmt_keys (dict[str, str] | None): A dictionary where keys are the
                desired names in the JSON output and values are the corresponding
                attribute names on the `logging.LogRecord` object.
        """
        super().__init__()
        self.fmt_keys = fmt_keys or {}

    @override
    def format(self, record: logging.LogRecord) -> str:
        """Formats a log record into a JSON string.

        Args:
            record (logging.LogRecord): The log record to format.

        Returns:
            str: A JSON string representation of the log record.
        """
        structlog: dict[str, Any] = self._create_structlog(record)
        return json.dumps(structlog, default=str)

    def _create_structlog(
        self,
        record: logging.LogRecord,
    ) -> dict[str, Any]:
        """Creates a dictionary from a log record for JSON serialization.

        Any extra attributes passed to the logger will be automatically included.

        Args:
            record (logging.LogRecord): The log record to process.

        Returns:
            dict[str, Any]: A dictionary containing the structured log information.
        """

        # certain log record attributes require special treatment #
        special_attrs: dict[str, Any] = {}
        special_attrs["message"] = record.getMessage()
        special_attrs["timestamp"] = dt.datetime.fromtimestamp(
            record.created, tz=dt.UTC
        ).isoformat()

        if record.exc_info is not None:
            special_attrs["exc_info"] = self.formatException(record.exc_info)

        if record.stack_info is not None:
            special_attrs["stack_info"] = self.formatStack(record.stack_info)

        structlog: dict[str, Any] = {}
        for out_name, attr_name in self.fmt_keys.items():
            if attr_name in special_attrs:
                structlog[out_name] = special_attrs[attr_name]
            else:
                structlog[out_name] = getattr(record, attr_name, None)

        # Add any "extra" attributes from the log record. These are attributes
        # that are not part of the standard LogRecord and were not already
        # processed via fmt_keys.
        processed_attrs: set[str] = set(self.fmt_keys.values())
        for attr_name, attr_value in record.__dict__.items():
            if (
                attr_name not in _RESERVED_LOG_RECORD_ATTRS
                and attr_name not in processed_attrs
            ):
                structlog[attr_name] = attr_value

        return structlog
