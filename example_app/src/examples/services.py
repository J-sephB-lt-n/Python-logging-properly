"""
Toy services used in the examples.
"""

import json
import logging
import time

from src.logging_utils import log_session

logger: logging.Logger = logging.getLogger(__name__)


def some_function() -> str:
    """Function containing a logging session."""
    with log_session(some_function_session_id=80085) as log_sess:
        start_time = time.perf_counter()
        logger.info("Started request")
        log_sess.joe = {"is": "ok"}
        logger.info(
            "Finished request",
            extra={"request_duration": time.perf_counter() - start_time},
        )

        return "something rude"


def imagine_this_is_an_http_request(parent_log_session: str) -> bool:
    """
    Function which gets logging session context as a JSON string.
    (e.g. it can be included as an HTTP header to an external service.
    """
    with log_session(
        **json.loads(parent_log_session),
        service_name="some_external_service",
    ) as log_sess:
        start_time = time.perf_counter()
        logger.info("Started request")
        log_sess.what = ["happens", "now", "?"]
        logger.info(
            "Finished request",
            extra={"request_duration": time.perf_counter() - start_time},
        )

        return True
