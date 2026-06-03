"""FastAPI application for the read-only Hermes UI MVP."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse

from backend.config import get_settings
from backend.log_sources import DEFAULT_LOG_LINES, MAX_LOG_LINES
from backend.logs import get_log_content, get_logs_sources_payload
from backend.status import get_hermes_status, get_service_status, get_system_status

app = FastAPI(
    title="Hermes UI for Bob",
    description="Read-only local control panel foundation for Hermes/Bob.",
    version="0.1.0",
)


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def dashboard() -> str:
    return """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Hermes UI for Bob</title>
  <style>
    :root {
      color-scheme: light;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: #f6f7f9;
      color: #151922;
    }
    body {
      margin: 0;
      padding: 32px;
    }
    main {
      max-width: 1080px;
      margin: 0 auto;
    }
    header {
      margin-bottom: 24px;
    }
    h1 {
      margin: 0 0 8px;
      font-size: 2rem;
    }
    .subtle {
      color: #5b6472;
    }
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 16px;
    }
    .card {
      background: #ffffff;
      border: 1px solid #dfe3ea;
      border-radius: 16px;
      box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
      padding: 20px;
    }
    .card h2 {
      margin: 0 0 12px;
      font-size: 1.1rem;
    }
    pre {
      white-space: pre-wrap;
      word-break: break-word;
      background: #f1f4f8;
      border-radius: 12px;
      padding: 12px;
      font-size: 0.85rem;
      overflow: auto;
    }
    .notice {
      border-left: 4px solid #2563eb;
      background: #eff6ff;
      padding: 12px 14px;
      border-radius: 12px;
      margin-top: 20px;
    }
    .logs-grid {
      margin-top: 20px;
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: 16px;
    }
  </style>
</head>
<body>
  <main>
    <header>
      <h1>Hermes UI for Bob</h1>
      <p class="subtle">Read-only MVP: status, Hermes status, system information, and bounded logs.</p>
    </header>
    <section class="grid">
      <article class="card">
        <h2>Hermes UI</h2>
        <pre id="service">Loading...</pre>
      </article>
      <article class="card">
        <h2>Hermes Gateway</h2>
        <pre id="hermes">Loading...</pre>
      </article>
      <article class="card">
        <h2>Bob / System</h2>
        <pre id="system">Loading...</pre>
      </article>
    </section>
    <section class="logs-grid">
      <article class="card">
        <h2>Log Sources</h2>
        <pre id="log-sources">Loading...</pre>
      </article>
      <article class="card">
        <h2>Gateway Output</h2>
        <pre id="log-stdout">Loading...</pre>
      </article>
      <article class="card">
        <h2>Gateway Errors</h2>
        <pre id="log-stderr">Loading...</pre>
      </article>
    </section>
    <section class="notice">
      Logs are read-only from server-side allowlisted sources. Start, stop, restart,
      and terminal access remain unavailable.
    </section>
  </main>
  <script>
    async function render(id, path) {
      const target = document.getElementById(id);
      try {
        const response = await fetch(path);
        const payload = await response.json();
        target.textContent = JSON.stringify(payload, null, 2);
      } catch (error) {
        target.textContent = JSON.stringify({ ok: false, error: String(error) }, null, 2);
      }
    }
    render("service", "/api/status");
    render("hermes", "/api/hermes/status");
    render("system", "/api/system");
    render("log-sources", "/api/logs/sources");
    render("log-stdout", "/api/logs/gateway_stdout?lines=50");
    render("log-stderr", "/api/logs/gateway_stderr?lines=50");
  </script>
</body>
</html>
"""


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

