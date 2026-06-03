"""Runtime configuration for the read-only Hermes UI backend."""

from __future__ import annotations

import os
from dataclasses import dataclass


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default

    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    env: str = "development"
    host: str = "127.0.0.1"
    port: int = 8787
    service_name: str = "hermes-ui"
    version: str = "0.1.0"
    bob_hostname: str = ""
    hermes_launchd_label: str = "ai.hermes.gateway"
    allow_unsafe_commands: bool = False


def get_settings() -> Settings:
    """Load settings from environment variables with safe read-only defaults."""
    return Settings(
        env=os.getenv("HERMES_UI_ENV", "development"),
        host=os.getenv("HERMES_UI_HOST", "127.0.0.1"),
        port=int(os.getenv("HERMES_UI_PORT", "8787")),
        bob_hostname=os.getenv("BOB_HOSTNAME", ""),
        hermes_launchd_label=os.getenv("HERMES_LAUNCHD_LABEL", "ai.hermes.gateway"),
        allow_unsafe_commands=_env_bool("ALLOW_UNSAFE_COMMANDS", False),
    )

