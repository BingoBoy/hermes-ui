"""FastAPI application for the read-only Hermes UI MVP."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse

from backend.config import get_settings
from backend.dashboard import render_dashboard
from backend.log_sources import DEFAULT_LOG_LINES, MAX_LOG_LINES
from backend.logs import get_log_content, get_logs_sources_payload
from backend.service_actions import (
    ActionNotAllowed,
    CooldownActive,
    ServiceActionsDisabled,
    build_restart_response,
)
from backend.status import get_hermes_status, get_service_status, get_system_status

app = FastAPI(
    title="Hermes UI for Bob",
    description="Read-only local control panel foundation for Hermes/Bob.",
    version="0.1.0",
)


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def dashboard() -> str:
    return render_dashboard()


@app.get("/api/status")
def api_status() -> dict:
    settings = get_settings()
    return get_service_status(settings)


@app.get("/api/system")
def api_system() -> dict:
    settings = get_settings()
    return get_system_status(settings)


@app.get("/api/hermes/status")
def api_hermes_status() -> dict:
    settings = get_settings()
    return get_hermes_status(settings)


@app.post("/api/hermes/restart")
def api_hermes_restart():
    settings = get_settings()
    try:
        payload = build_restart_response(settings)
    except ServiceActionsDisabled:
        raise HTTPException(
            status_code=403,
            detail={
                "success": False,
                "error": "service_actions_disabled",
                "detail": "Write actions are disabled on this server",
            },
        ) from None
    except CooldownActive as exc:
        raise HTTPException(
            status_code=429,
            detail={
                "success": False,
                "error": "cooldown_active",
                "detail": f"Restart was requested recently; try again in {exc.retry_after} seconds",
                "retry_after": exc.retry_after,
            },
        ) from None
    except ActionNotAllowed as exc:
        raise HTTPException(
            status_code=404,
            detail={
                "success": False,
                "error": "action_not_allowed",
                "detail": str(exc),
            },
        ) from None

    if not payload["success"]:
        return JSONResponse(status_code=502, content=payload)
    return payload


@app.get("/api/logs/sources")
def api_logs_sources() -> dict:
    return get_logs_sources_payload()


@app.get("/api/logs/{source_id}")
def api_logs_source(
    source_id: str,
    lines: int = Query(default=DEFAULT_LOG_LINES, ge=1, le=MAX_LOG_LINES),
) -> dict:
    payload = get_log_content(source_id, lines)
    if payload is None:
        raise HTTPException(
            status_code=404,
            detail={
                "success": False,
                "error": "unknown_log_source",
                "details": f"Unknown or disabled log source: {source_id}",
            },
        )
    return payload

