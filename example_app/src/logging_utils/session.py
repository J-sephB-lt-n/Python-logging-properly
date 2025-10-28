"""
Code for automatically injecting context-scoped variables into the `extra` attribute
of every logging call within the context.
"""

from contextlib import contextmanager
from contextvars import ContextVar
from types import MappingProxyType, SimpleNamespace

_log_session_vars: ContextVar[MappingProxyType | None] = ContextVar(
    "_log_session_vars",
    default=None,
)


@contextmanager
def log_session(**kwargs):
    """
    Context manager which persists session variables.
    """
    existing_session_vars: MappingProxyType = (
        _log_session_vars.get() or MappingProxyType({})
    )
    session_vars = SimpleNamespace(
        **(dict(existing_session_vars) | kwargs),
    )
    _session_vars_token = _log_session_vars.set(
        MappingProxyType(session_vars.__dict__),
    )
    try:
        yield session_vars
    finally:
        _log_session_vars.reset(_session_vars_token)
