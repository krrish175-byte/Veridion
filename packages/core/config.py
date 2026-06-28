"""Application configuration via pydantic-settings.

Values are loaded from environment variables — never hardcoded or
auto-instantiated at import time.  Callers obtain a Settings instance through
the ``get_settings()`` factory and inject it where needed.
"""

from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Root configuration for the Veridion platform.

    Every field maps 1-to-1 to an environment variable of the same
    (upper-cased) name — e.g. ``APP_ENV``, ``LOG_LEVEL``.
    """

    app_env: str = "local"
    log_level: str = "INFO"
    postgres_url: str = (
        "postgresql://veridion:veridion@localhost:5432/veridion"
    )
    redis_url: str = "redis://localhost:6379/0"

    model_config = {"env_prefix": ""}


def get_settings() -> Settings:
    """Factory — returns a *new* Settings instance each time.

    Callers should inject the returned object rather than relying on a
    module-level singleton.
    """
    return Settings()
