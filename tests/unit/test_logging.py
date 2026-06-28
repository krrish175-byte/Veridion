"""Unit tests for packages.core.logging."""

from __future__ import annotations

import json
import logging

from packages.core.logging import correlation_id, get_logger


class TestGetLogger:
    """get_logger() returns a properly configured JSON-emitting logger."""

    def test_returns_logger(self) -> None:
        logger = get_logger("test.returns")
        assert isinstance(logger, logging.Logger)

    def test_logger_name(self) -> None:
        logger = get_logger("test.name")
        assert logger.name == "test.name"


class TestJSONOutput:
    """Log output is valid JSON with the required fields."""

    def _capture_log(self, logger: logging.Logger, message: str) -> dict:
        """Emit a log record and return the parsed JSON payload."""
        handler = logger.handlers[0]
        record = logger.makeRecord(
            name=logger.name,
            level=logging.INFO,
            fn="",
            lno=0,
            msg=message,
            args=(),
            exc_info=None,
        )
        output = handler.format(record)
        return json.loads(output)

    def test_output_is_valid_json(self) -> None:
        logger = get_logger("test.json_valid")
        payload = self._capture_log(logger, "hello")
        assert isinstance(payload, dict)

    def test_required_fields_present(self) -> None:
        logger = get_logger("test.fields")
        payload = self._capture_log(logger, "check fields")
        for key in ("timestamp", "level", "logger", "message", "correlation_id"):
            assert key in payload, f"Missing key: {key}"

    def test_message_content(self) -> None:
        logger = get_logger("test.msg")
        payload = self._capture_log(logger, "specific message")
        assert payload["message"] == "specific message"

    def test_level_field(self) -> None:
        logger = get_logger("test.level")
        payload = self._capture_log(logger, "level check")
        assert payload["level"] == "INFO"

    def test_logger_field(self) -> None:
        logger = get_logger("test.logger_field")
        payload = self._capture_log(logger, "logger check")
        assert payload["logger"] == "test.logger_field"


class TestCorrelationId:
    """correlation_id context variable appears in log output."""

    def _capture_log(self, logger: logging.Logger, message: str) -> dict:
        handler = logger.handlers[0]
        record = logger.makeRecord(
            name=logger.name,
            level=logging.INFO,
            fn="",
            lno=0,
            msg=message,
            args=(),
            exc_info=None,
        )
        return json.loads(handler.format(record))

    def test_default_correlation_id_is_none(self) -> None:
        token = correlation_id.set(None)
        try:
            logger = get_logger("test.corr_none")
            payload = self._capture_log(logger, "no id")
            assert payload["correlation_id"] is None
        finally:
            correlation_id.reset(token)

    def test_correlation_id_propagates(self) -> None:
        token = correlation_id.set("req-abc-123")
        try:
            logger = get_logger("test.corr_set")
            payload = self._capture_log(logger, "with id")
            assert payload["correlation_id"] == "req-abc-123"
        finally:
            correlation_id.reset(token)

    def test_correlation_id_changes(self) -> None:
        token1 = correlation_id.set("id-1")
        try:
            logger = get_logger("test.corr_change")
            p1 = self._capture_log(logger, "first")
            assert p1["correlation_id"] == "id-1"

            token2 = correlation_id.set("id-2")
            try:
                p2 = self._capture_log(logger, "second")
                assert p2["correlation_id"] == "id-2"
            finally:
                correlation_id.reset(token2)
        finally:
            correlation_id.reset(token1)
