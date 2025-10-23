"""
Functions for global logging setup.
"""

import atexit
import logging
import logging.config
from pathlib import Path

import yaml


def setup_logging() -> None:
    """Once-off global setup of application logging."""
    config_file = Path("./config/logging_config.yaml")
    with config_file.open("r", encoding="utf-8") as file:
        config: dict = yaml.safe_load(file)

    logging.config.dictConfig(config)

    queue_handler = logging.getHandlerByName("queue_handler")
    queue_handler.listener.start()
    atexit.register(queue_handler.listener.stop)
