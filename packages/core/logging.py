"""Structured JSON logging with per-request correlation IDs.

Usage::

    from packages.core.logging import get_logger, correlation_id

    logger = get_logger(__name__)
    correlation_id.set("req-abc-123")
    logger.info("processing started")
    # => {"timestamp": "...", "level": "INFO", "logger": "...",
    #     "message": "processing started", "correlation_id": "req-abc-123"}

The ``correlation_id`` context-variable can be bound once per request or
task (e.g. in middleware) and automatically appears in every subsequent log
line without touching individual call-sites.
"""

from __future__ import annotations

import json
import logging
from contextvars import ContextVar
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Context variable — bind once per request / task
# ---------------------------------------------------------------------------
correlation_id: ContextVar[str | None] = ContextVar(
    "correlation_id", default=None
)


# ---------------------------------------------------------------------------
# Custom JSON formatter
# ---------------------------------------------------------------------------
class _JSONFormatter(logging.Formatter):
    """Emits one JSON object per log record."""

    def format(self, record: logging.LogRecord) -> str:  # noqa: D401
        payload = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "correlation_id": correlation_id.get(),
        }
        return json.dumps(payload, default=str)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
_CONFIGURED_LOGGERS: set[str] = set()


def get_logger(name: str) -> logging.Logger:
    """Return a stdlib logger that emits structured JSON to *stderr*.

    The logger is configured at most once per *name*; subsequent calls for
    the same name return the cached logger with its handler already attached.
    """
    logger = logging.getLogger(name)

    if name not in _CONFIGURED_LOGGERS:
        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        handler.setFormatter(_JSONFormatter())
        logger.addHandler(handler)
        logger.propagate = False
        _CONFIGURED_LOGGERS.add(name)

    return logger
