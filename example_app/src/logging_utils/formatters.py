"""Custom logging formatters."""

import datetime as dt
import json
import logging
import os
from typing import Any, override

from rich.console import Console
from rich.highlighter import JSONHighlighter
from rich.text import Text

_RESERVED_LOG_RECORD_ATTRS = frozenset(
    # from https://docs.python.org/3/library/logging.html#logrecord-attributes
    (
        "args",
        "asctime",
        "created",
        "exc_info",
        "exc_text",
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

LOG_LEVEL_STYLES = {
    # used to colour logs in stdout when DEV_LOGGING=true #
    "DEBUG": "cyan",
    "INFO": "green",
    "WARNING": "yellow",
    "ERROR": "red",
    "CRITICAL": "bold red",
}


class JsonLogFormatter(logging.Formatter):
    """A logging formatter that outputs log records as JSON strings."""

    def __init__(
        self,
        *,
        fmt_keys: dict[str, str] | None = None,
        colourise: bool = False,
        indent: bool = False,
    ) -> None:
        """
        Initializes the JsonLogFormatter.

        Args:
            fmt_keys (dict[str, str] | None): A dictionary where keys are the
                desired names in the JSON output and values are the corresponding
                attribute names on the `logging.LogRecord` object.
            colourise (bool, default=False): Whether to output colourful JSON. This is only
                applied when the `DEV_LOGGING` environment variable is set to "true".
            indent (bool, default=False): Whether to output indented JSON. This is only
                applied when the `DEV_LOGGING` environment variable is set to "true".
        """
        super().__init__()
        self.fmt_keys = fmt_keys or {}
        self.colourise = colourise
        self.indent = indent

    @override
    def format(self, record: logging.LogRecord) -> str:
        """Formats `record` into a JSON string."""
        structlog: dict[str, Any] = self._create_structlog(record)

        if os.environ.get("DEV_LOGGING") == "true":
            if self.indent:
                json_str = json.dumps(structlog, indent=4)
            else:
                json_str = json.dumps(structlog)

            if self.colourise:
                console = Console()
                text = Text(json_str)
                JSONHighlighter().highlight(text)

                level_name = record.levelname
                if level_style := LOG_LEVEL_STYLES.get(level_name):
                    level_key: str | None = None
                    for key, value in self.fmt_keys.items():
                        if value == "levelname":
                            level_key = key
                            break

                    if level_key:
                        text.highlight_regex(
                            rf'"{level_key}"\s*:\s*("{level_name}")',
                            style=level_style,
                        )

                with console.capture() as capture:
                    console.print(text)
                return capture.get().strip()

        return json.dumps(structlog)

    def _create_structlog(
        self,
        record: logging.LogRecord,
    ) -> dict[str, Any]:
        """
        Creates a dictionary from a log record for JSON serialization.
        Any extra attributes passed to the logger are automatically included.
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
                structlog[out_name] = getattr(record, attr_name)

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
