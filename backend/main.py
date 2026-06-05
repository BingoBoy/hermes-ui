"""FastAPI application for the read-only Hermes UI MVP."""

from __future__ import annotations

from pydantic import BaseModel, Field

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse

from backend.bob_tasks import (
    BobTasksDisabled,
    CooldownActive as BobCooldownActive,
    InvalidTaskAssigneeConfig,
    InvalidTaskId,
    InvalidTaskInput,
    TaskNotFound,
    build_task_create_response,
    build_task_list_response,
    build_task_show_response,
)
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
from backend.operations import get_operations_status
from backend.site_search import SiteSearchError, SiteSearchInput, search_public_website
from backend.status import get_hermes_status, get_service_status, get_system_status


class BobTaskRequest(BaseModel):
    title: str = Field(..., min_length=1)
    body: str = ""

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


@app.get("/api/operations")
def api_operations() -> dict:
    settings = get_settings()
    return get_operations_status(settings)


@app.get("/api/site-search")
async def api_site_search(
    site_url: str = Query(..., alias="siteUrl", min_length=1),
    query: str = Query(..., min_length=1),
) -> dict:
    try:
        return await search_public_website(
            SiteSearchInput(site_url=site_url, query=query)
        )
    except SiteSearchError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail={
                "success": False,
                "error": exc.error,
                "detail": exc.detail,
            },
        ) from None


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


@app.post("/api/bob/tasks", status_code=202)
def api_bob_create_task(request: BobTaskRequest):
    settings = get_settings()
    try:
        payload = build_task_create_response(
            settings,
            title=request.title,
            body=request.body or None,
        )
    except BobTasksDisabled:
        raise HTTPException(
            status_code=403,
            detail={
                "success": False,
                "error": "bob_tasks_disabled",
                "detail": "Bob task entry is disabled on this server",
            },
        ) from None
    except InvalidTaskInput as exc:
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error": "invalid_input",
                "detail": str(exc),
            },
        ) from None
    except BobCooldownActive as exc:
        raise HTTPException(
            status_code=429,
            detail={
                "success": False,
                "error": "cooldown_active",
                "detail": (
                    f"Task was submitted recently; try again in {exc.retry_after} seconds"
                ),
                "retry_after": exc.retry_after,
            },
        ) from None
    except InvalidTaskAssigneeConfig as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": "invalid_bob_task_assignee_config",
                "detail": str(exc),
            },
        ) from None

    if not payload["success"]:
        return JSONResponse(status_code=502, content=payload)
    return JSONResponse(status_code=202, content=payload)


@app.get("/api/bob/tasks")
def api_bob_list_tasks(
    limit: int = Query(default=20, ge=1, le=50),
):
    settings = get_settings()
    try:
        payload = build_task_list_response(settings, limit=limit)
    except BobTasksDisabled:
        raise HTTPException(
            status_code=403,
            detail={
                "success": False,
                "error": "bob_tasks_disabled",
                "detail": "Bob task access is disabled on this server",
            },
        ) from None

    if not payload["success"]:
        return JSONResponse(status_code=502, content=payload)
    return payload


@app.get("/api/bob/tasks/{task_id}")
def api_bob_show_task(task_id: str):
    settings = get_settings()
    try:
        payload = build_task_show_response(settings, task_id)
    except BobTasksDisabled:
        raise HTTPException(
            status_code=403,
            detail={
                "success": False,
                "error": "bob_tasks_disabled",
                "detail": "Bob task access is disabled on this server",
            },
        ) from None
    except InvalidTaskId as exc:
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error": "invalid_task_id",
                "detail": str(exc),
            },
        ) from None
    except TaskNotFound:
        raise HTTPException(
            status_code=404,
            detail={
                "success": False,
                "error": "task_not_found",
                "detail": f"Task not found: {task_id}",
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
