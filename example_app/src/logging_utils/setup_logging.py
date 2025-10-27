"""
Functions for global logging setup.
"""

import atexit
import logging
import logging.config
from pathlib import Path
from types import MappingProxyType

import yaml

from src.logging_utils.session import _log_session_vars


def setup_logging() -> None:
    """Once-off global setup of application logging."""
    config_file = Path("./config/logging_config.yaml")
    with config_file.open("r", encoding="utf-8") as file:
        config: dict = yaml.safe_load(file)

    logging.config.dictConfig(config)

    old_record_factory = logging.getLogRecordFactory()

    def record_factory(*args, **kwargs):
        record = old_record_factory(*args, **kwargs)
        session_vars: MappingProxyType | None = _log_session_vars.get()
        if session_vars:
            for key, value in session_vars.items():
                if hasattr(record, key):
                    raise AttributeError(
                        f"Cannot overwrite existing attribute '{key}' on log record."
                    )
                setattr(record, key, value)
        return record

    logging.setLogRecordFactory(record_factory)

    queue_handler = logging.getHandlerByName("queue_handler")
    queue_handler.listener.start()
    atexit.register(queue_handler.listener.stop)
