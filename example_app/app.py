"""
Main entrypoint of the application.
"""

import logging

from src.logging_utils import setup_logging


def main():
    setup_logging()

    logger = logging.getLogger(__name__)

    logger.debug("This is a debug message", extra={"something extra": "in debug"})
    logger.info("This is an info message", extra={"something extra": "in info"})
    logger.warning("This is a warning message", extra={"something extra": "in warning"})
    logger.error("This is an error message", extra={"something extra": "in error"})
    logger.critical(
        "This is a critical message", extra={"something extra": "in critical"}
    )


if __name__ == "__main__":
    main()
