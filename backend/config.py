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
    hermes_ui_launchd_label: str = "no.truls.hermes-ui"
    hermes_ui_plist_path: str = (
        "~/Library/LaunchAgents/no.truls.hermes-ui.plist"
    )
    hermes_gateway_plist_path: str = (
        "~/Library/LaunchAgents/ai.hermes.gateway.plist"
    )
    hermes_ops_include_docker: bool = False
    hermes_public_hostname: str = "hermes-ui.strategistudio.no"
    hermes_cloudflare_tunnel_name: str = "bob-mac-mini-m4"
    hermes_ops_edge_probe: bool = True
    hermes_cloudflared_bin: str = "/opt/homebrew/bin/cloudflared"
    hermes_cloudflared_launchd_label: str = ""
    allow_unsafe_commands: bool = False
    allow_service_actions: bool = False
    allow_bob_tasks: bool = False
    hermes_cli_bin: str = "/Users/trulsdahl/.hermes/hermes-agent/venv/bin/hermes"
    bob_task_timeout_seconds: float = 30.0
    bob_task_assignee: str = ""


def get_settings() -> Settings:
    """Load settings from environment variables with safe read-only defaults."""
    return Settings(
        env=os.getenv("HERMES_UI_ENV", "development"),
        host=os.getenv("HERMES_UI_HOST", "127.0.0.1"),
        port=int(os.getenv("HERMES_UI_PORT", "8787")),
        bob_hostname=os.getenv("BOB_HOSTNAME", ""),
        hermes_launchd_label=os.getenv("HERMES_LAUNCHD_LABEL", "ai.hermes.gateway"),
        hermes_ui_launchd_label=os.getenv(
            "HERMES_UI_LAUNCHD_LABEL", "no.truls.hermes-ui"
        ).strip()
        or "no.truls.hermes-ui",
        hermes_ui_plist_path=os.getenv(
            "HERMES_UI_PLIST_PATH",
            "~/Library/LaunchAgents/no.truls.hermes-ui.plist",
        ).strip()
        or "~/Library/LaunchAgents/no.truls.hermes-ui.plist",
        hermes_gateway_plist_path=os.getenv(
            "HERMES_GATEWAY_PLIST_PATH",
            "~/Library/LaunchAgents/ai.hermes.gateway.plist",
        ).strip()
        or "~/Library/LaunchAgents/ai.hermes.gateway.plist",
        hermes_ops_include_docker=_env_bool("HERMES_OPS_INCLUDE_DOCKER", False),
        hermes_public_hostname=os.getenv(
            "HERMES_PUBLIC_HOSTNAME", "hermes-ui.strategistudio.no"
        ).strip()
        or "hermes-ui.strategistudio.no",
        hermes_cloudflare_tunnel_name=os.getenv(
            "HERMES_CLOUDFLARE_TUNNEL_NAME", "bob-mac-mini-m4"
        ).strip()
        or "bob-mac-mini-m4",
        hermes_ops_edge_probe=_env_bool("HERMES_OPS_EDGE_PROBE", True),
        hermes_cloudflared_bin=os.getenv(
            "HERMES_CLOUDFLARED_BIN", "/opt/homebrew/bin/cloudflared"
        ).strip()
        or "/opt/homebrew/bin/cloudflared",
        hermes_cloudflared_launchd_label=os.getenv(
            "HERMES_CLOUDFLARED_LAUNCHD_LABEL", ""
        ).strip(),
        allow_unsafe_commands=_env_bool("ALLOW_UNSAFE_COMMANDS", False),
        allow_service_actions=_env_bool("ALLOW_SERVICE_ACTIONS", False),
        allow_bob_tasks=_env_bool("ALLOW_BOB_TASKS", False),
        hermes_cli_bin=os.getenv("HERMES_CLI_BIN", Settings.hermes_cli_bin).strip()
        or Settings.hermes_cli_bin,
        bob_task_timeout_seconds=float(
            os.getenv("BOB_TASK_TIMEOUT_SECONDS", "30").strip() or "30"
        ),
        bob_task_assignee=os.getenv("HERMES_BOB_TASK_ASSIGNEE", "").strip(),
    )
