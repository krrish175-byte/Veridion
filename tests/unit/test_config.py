"""Unit tests for packages.core.config."""

from __future__ import annotations

import os

from packages.core.config import Settings, get_settings


class TestSettingsDefaults:
    """Settings loads with sane defaults when no env vars are set."""

    def test_default_app_env(self) -> None:
        settings = get_settings()
        assert settings.app_env == "local"

    def test_default_log_level(self) -> None:
        settings = get_settings()
        assert settings.log_level == "INFO"

    def test_default_postgres_url(self) -> None:
        settings = get_settings()
        assert settings.postgres_url == (
            "postgresql://veridion:veridion@localhost:5432/veridion"
        )

    def test_default_redis_url(self) -> None:
        settings = get_settings()
        assert settings.redis_url == "redis://localhost:6379/0"


class TestSettingsEnvOverride:
    """Settings respects environment variable overrides."""

    def test_app_env_from_env(self, monkeypatch: object) -> None:
        os.environ["APP_ENV"] = "production"
        try:
            settings = get_settings()
            assert settings.app_env == "production"
        finally:
            del os.environ["APP_ENV"]

    def test_log_level_from_env(self, monkeypatch: object) -> None:
        os.environ["LOG_LEVEL"] = "DEBUG"
        try:
            settings = get_settings()
            assert settings.log_level == "DEBUG"
        finally:
            del os.environ["LOG_LEVEL"]

    def test_postgres_url_from_env(self) -> None:
        custom = "postgresql://user:pass@db:5432/mydb"
        os.environ["POSTGRES_URL"] = custom
        try:
            settings = get_settings()
            assert settings.postgres_url == custom
        finally:
            del os.environ["POSTGRES_URL"]

    def test_redis_url_from_env(self) -> None:
        custom = "redis://cache:6379/1"
        os.environ["REDIS_URL"] = custom
        try:
            settings = get_settings()
            assert settings.redis_url == custom
        finally:
            del os.environ["REDIS_URL"]


class TestGetSettingsFactory:
    """get_settings() returns a new instance each time — no singleton."""

    def test_returns_new_instance(self) -> None:
        a = get_settings()
        b = get_settings()
        assert a is not b
        assert a == b  # same values when env hasn't changed

    def test_returns_settings_type(self) -> None:
        assert isinstance(get_settings(), Settings)
