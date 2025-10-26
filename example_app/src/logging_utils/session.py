"""
Code for automatically injecting context-scoped variables into the `extra` attribute
of every logging call within the context.
"""

import logging
from contextlib import contextmanager, asynccontextmanager
from contextvars import ContextVar
from types import MappingProxyType, SimpleNamespace
from typing import override

_log_session_vars: ContextVar[MappingProxyType | None] = ContextVar(
    "_log_session_vars",
    default=None,
)


class AddLogSessionContextVars(logging.Filter):
    """
    Filter which adds variables scoped to the log session context
    into the log record.
    """

    @override
    def filter(self, record: logging.LogRecord) -> bool:
        """TODO."""
        session_vars: MappingProxyType | None = _log_session_vars.get()
        if hasattr(record, "log_session"):
            raise AttributeError(
                "'log_session' is an attribute name in log records reserved for "
                + "the log_session() context manager."
            )
        if session_vars:
            record.log_session = dict(session_vars)
        return True


@contextmanager
def log_session(**kwargs):
    """
    Context manager which persists session variables.
    """
    session_vars = SimpleNamespace(**kwargs)
    _session_vars_token = _log_session_vars.set(
        MappingProxyType(session_vars.__dict__),
    )
    try:
        yield session_vars
    finally:
        _log_session_vars.reset(_session_vars_token)


# @asynccontextmanager
# def AsyncLogSession(): ...
#     """TODO"""
