"""
Main entrypoint of the application.
"""

import logging

from src.logging_utils import setup_logging


def main():
    setup_logging()

    logger = logging.getLogger(__name__)

    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")


if __name__ == "__main__":
    main()
