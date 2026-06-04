"""Read-only dashboard HTML for Hermes UI."""

from __future__ import annotations

DASHBOARD_HTML = """\
<!doctype html>
<html lang="no">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Hermes UI for Bob</title>
  <style>
    :root {
      color-scheme: light;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: #f3f5f8;
      color: #151922;
      --ok: #15803d;
      --ok-bg: #dcfce7;
      --warn: #b45309;
      --warn-bg: #fef3c7;
      --bad: #b91c1c;
      --bad-bg: #fee2e2;
      --muted: #5b6472;
      --border: #dfe3ea;
      --card: #ffffff;
    }
    * { box-sizing: border-box; }
    body { margin: 0; padding: 24px; }
    main { max-width: 1120px; margin: 0 auto; }
    header {
      display: flex;
      flex-wrap: wrap;
      align-items: flex-start;
      justify-content: space-between;
      gap: 16px;
      margin-bottom: 24px;
    }
    h1 { margin: 0 0 6px; font-size: 1.85rem; }
    .subtle { color: var(--muted); margin: 0; }
    .toolbar {
      display: flex;
      align-items: center;
      gap: 12px;
      flex-wrap: wrap;
    }
    button {
      border: 1px solid var(--border);
      background: var(--card);
      color: inherit;
      border-radius: 10px;
      padding: 10px 14px;
      font: inherit;
      cursor: pointer;
    }
    button:hover { background: #eef2f7; }
    .updated { color: var(--muted); font-size: 0.9rem; }
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 16px;
      margin-bottom: 20px;
    }
    .card {
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 16px;
      box-shadow: 0 8px 24px rgba(15, 23, 42, 0.05);
      padding: 18px;
    }
    .card h2 {
      margin: 0 0 10px;
      font-size: 1rem;
      color: var(--muted);
      font-weight: 600;
    }
    .status-row {
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 12px;
    }
    .badge {
      display: inline-flex;
      align-items: center;
      border-radius: 999px;
      padding: 4px 10px;
      font-size: 0.85rem;
      font-weight: 600;
      white-space: nowrap;
    }
    .badge.ok { background: var(--ok-bg); color: var(--ok); }
    .badge.warn { background: var(--warn-bg); color: var(--warn); }
    .badge.bad { background: var(--bad-bg); color: var(--bad); }
    .meta { margin: 0; font-size: 0.92rem; line-height: 1.5; }
    .meta dt {
      color: var(--muted);
      font-size: 0.78rem;
      text-transform: uppercase;
      letter-spacing: 0.03em;
      margin-top: 8px;
    }
    .meta dd { margin: 2px 0 0; }
    details {
      margin-top: 12px;
      border-top: 1px solid #eef1f5;
      padding-top: 10px;
    }
    summary {
      cursor: pointer;
      color: var(--muted);
      font-size: 0.85rem;
      user-select: none;
    }
    pre {
      white-space: pre-wrap;
      word-break: break-word;
      background: #f1f4f8;
      border-radius: 10px;
      padding: 10px;
      font-size: 0.78rem;
      overflow: auto;
      max-height: 220px;
      margin: 8px 0 0;
    }
    .logs-section h2 {
      margin: 0 0 16px;
      font-size: 1.15rem;
    }
    .logs-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
      gap: 16px;
    }
    .log-panel h3 {
      margin: 0 0 8px;
      font-size: 1rem;
    }
    .log-meta {
      color: var(--muted);
      font-size: 0.85rem;
      margin: 0 0 10px;
    }
    .log-view {
      background: #0f172a;
      color: #e2e8f0;
      border-radius: 12px;
      padding: 12px;
      font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
      font-size: 0.78rem;
      line-height: 1.45;
      max-height: 320px;
      overflow: auto;
      margin: 0;
    }
    .log-view .line { display: block; padding: 1px 0; white-space: pre-wrap; word-break: break-word; }
    .log-view .empty { color: #94a3b8; font-style: italic; }
    .notice {
      border-left: 4px solid #2563eb;
      background: #eff6ff;
      padding: 12px 14px;
      border-radius: 12px;
      margin-top: 20px;
      font-size: 0.92rem;
    }
    .error-text { color: var(--bad); font-size: 0.9rem; }
  </style>
</head>
<body>
  <main>
    <header>
      <div>
        <h1>Hermes UI for Bob</h1>
        <p class="subtle">Read-only kontrollpanel for status, gateway og bounded logger.</p>
      </div>
      <div class="toolbar">
        <button type="button" id="refresh-btn">Oppdater</button>
        <span class="updated" id="last-updated">Laster...</span>
      </div>
    </header>

    <section class="grid" aria-label="Statuskort">
      <article class="card" id="card-service">
        <h2>Hermes UI</h2>
        <div class="status-row">
          <span class="badge warn" id="service-badge">Laster</span>
        </div>
        <dl class="meta" id="service-meta"></dl>
        <details><summary>Teknisk JSON</summary><pre id="service-json">Loading...</pre></details>
      </article>

      <article class="card" id="card-hermes">
        <h2>Hermes Gateway</h2>
        <div class="status-row">
          <span class="badge warn" id="hermes-badge">Laster</span>
        </div>
        <dl class="meta" id="hermes-meta"></dl>
        <details><summary>Teknisk JSON</summary><pre id="hermes-json">Loading...</pre></details>
      </article>

      <article class="card" id="card-system">
        <h2>Bob / System</h2>
        <div class="status-row">
          <span class="badge warn" id="system-badge">Laster</span>
        </div>
        <dl class="meta" id="system-meta"></dl>
        <details><summary>Teknisk JSON</summary><pre id="system-json">Loading...</pre></details>
      </article>

      <article class="card" id="card-logs">
        <h2>Logger</h2>
        <div class="status-row">
          <span class="badge warn" id="logs-badge">Laster</span>
        </div>
        <dl class="meta" id="logs-meta"></dl>
        <details><summary>Teknisk JSON</summary><pre id="logs-json">Loading...</pre></details>
      </article>
    </section>

    <section class="logs-section">
      <h2>Gateway-logger</h2>
      <div class="logs-grid">
        <article class="card log-panel">
          <h3>Gateway Output</h3>
          <p class="log-meta" id="stdout-meta">Laster...</p>
          <div class="log-view" id="log-stdout" aria-live="polite"></div>
          <details><summary>Teknisk JSON</summary><pre id="stdout-json">Loading...</pre></details>
        </article>
        <article class="card log-panel">
          <h3>Gateway Errors</h3>
          <p class="log-meta" id="stderr-meta">Laster...</p>
          <div class="log-view" id="log-stderr" aria-live="polite"></div>
          <details><summary>Teknisk JSON</summary><pre id="stderr-json">Loading...</pre></details>
        </article>
      </div>
    </section>

    <section class="notice">
      Read-only MVP. Start, stopp, restart og terminal er ikke tilgjengelig.
      Oppdater siden manuelt eller bruk knappen over for å hente ny status.
    </section>
  </main>
  <script>
    function setBadge(id, label, tone) {
      const badge = document.getElementById(id);
      badge.textContent = label;
      badge.className = "badge " + tone;
    }

    function setMeta(id, rows) {
      const target = document.getElementById(id);
      target.innerHTML = rows.map(([key, value]) =>
        `<dt>${key}</dt><dd>${value ?? "—"}</dd>`
      ).join("");
    }

    function setJson(id, payload) {
      document.getElementById(id).textContent = JSON.stringify(payload, null, 2);
    }

    function renderLogLines(containerId, payload) {
      const container = document.getElementById(containerId);
      container.innerHTML = "";
      if (!payload || payload.success === false) {
        const empty = document.createElement("span");
        empty.className = "empty";
        empty.textContent = payload?.details || payload?.error || "Logg utilgjengelig";
        container.appendChild(empty);
        return;
      }
      const lines = payload.content || [];
      if (!lines.length) {
        const empty = document.createElement("span");
        empty.className = "empty";
        empty.textContent = "Ingen linjer i loggen";
        container.appendChild(empty);
        return;
      }
      for (const line of lines) {
        const row = document.createElement("span");
        row.className = "line";
        row.textContent = line;
        container.appendChild(row);
      }
    }

    async function fetchJson(path) {
      const response = await fetch(path);
      if (!response.ok) {
        let detail = response.statusText;
        try {
          const body = await response.json();
          detail = body.detail?.details || body.detail?.error || JSON.stringify(body.detail || body);
        } catch (_) {}
        return { ok: false, error: detail, status: response.status };
      }
      return { ok: true, data: await response.json() };
    }

    function renderService(payload) {
      if (!payload.ok) {
        setBadge("service-badge", "Offline", "bad");
        setMeta("service-meta", [["Status", "Kunne ikke hente status"]]);
        setJson("service-json", payload);
        return;
      }
      const data = payload.data;
      const online = data.status === "ok";
      setBadge("service-badge", online ? "Online" : "Offline", online ? "ok" : "bad");
      setMeta("service-meta", [
        ["Versjon", data.version],
        ["Host", data.host],
        ["Bind", `${data.bind_host}:${data.bind_port}`],
        ["Read-only", data.read_only ? "Ja" : "Nei"],
        ["Sjekket", data.checked_at],
      ]);
      setJson("service-json", data);
    }

    function renderHermes(payload) {
      if (!payload.ok) {
        setBadge("hermes-badge", "Ukjent", "bad");
        setMeta("hermes-meta", [["Status", "Kunne ikke hente gateway-status"]]);
        setJson("hermes-json", payload);
        return;
      }
      const data = payload.data;
      const running = !!data.running;
      setBadge("hermes-badge", running ? "Running" : "Not running", running ? "ok" : "warn");
      const launchctl = data.launchctl || {};
      const process = data.process || {};
      setMeta("hermes-meta", [
        ["State", data.state],
        ["LaunchAgent", launchctl.matched ? "Loaded" : "Not loaded"],
        ["Prosess", process.matched ? "Detected" : "Not detected"],
        ["Label", data.launchd_label || "—"],
        ["Sjekket", data.last_checked],
      ]);
      setJson("hermes-json", data);
    }

    function renderSystem(payload) {
      if (!payload.ok) {
        setBadge("system-badge", "Offline", "bad");
        setMeta("system-meta", [["Status", "Kunne ikke hente systeminfo"]]);
        setJson("system-json", payload);
        return;
      }
      const data = payload.data;
      setBadge("system-badge", "Online", "ok");
      setMeta("system-meta", [
        ["Hostname", data.hostname],
        ["Disk", data.disk?.percent_used ? `${data.disk.percent_used} brukt` : "—"],
        ["Minne", data.memory?.percent_used ? `${data.memory.percent_used} brukt` : "—"],
        ["Uptime", data.uptime || "—"],
        ["Sjekket", data.checked_at],
      ]);
      setJson("system-json", data);
    }

    function renderLogsSummary(sourcesPayload, stdoutPayload, stderrPayload) {
      if (!sourcesPayload.ok) {
        setBadge("logs-badge", "Unavailable", "bad");
        setMeta("logs-meta", [["Status", "Kunne ikke hente loggkilder"]]);
        setJson("logs-json", sourcesPayload);
        return;
      }
      const sources = sourcesPayload.data.sources || [];
      const stdoutOk = stdoutPayload.ok && stdoutPayload.data.success !== false;
      const stderrOk = stderrPayload.ok && stderrPayload.data.success !== false;
      const available = sources.length > 0 && (stdoutOk || stderrOk);
      setBadge("logs-badge", available ? "Available" : "Unavailable", available ? "ok" : "warn");
      setMeta("logs-meta", [
        ["Kilder", String(sources.length)],
        ["Gateway output", stdoutOk ? "OK" : "Utilgjengelig"],
        ["Gateway errors", stderrOk ? "OK" : "Utilgjengelig"],
      ]);
      setJson("logs-json", {
        sources: sourcesPayload.data,
        gateway_stdout: stdoutPayload.ok ? stdoutPayload.data : stdoutPayload,
        gateway_stderr: stderrPayload.ok ? stderrPayload.data : stderrPayload,
      });
    }

    function renderLogPanel(metaId, containerId, jsonId, payload) {
      const meta = document.getElementById(metaId);
      if (!payload.ok) {
        meta.textContent = "Kunne ikke hente logg";
        renderLogLines(containerId, { error: payload.error });
        setJson(jsonId, payload);
        return;
      }
      const data = payload.data;
      if (data.success === false) {
        meta.textContent = data.details || data.error || "Utilgjengelig";
        renderLogLines(containerId, data);
        setJson(jsonId, data);
        return;
      }
      meta.textContent = `${data.returned_lines || 0} linjer · ${data.display_name || data.source_id}`;
      renderLogLines(containerId, data);
      setJson(jsonId, data);
    }

    async function loadDashboard() {
      document.getElementById("last-updated").textContent = "Oppdaterer...";
      const [service, hermes, system, sources, stdout, stderr] = await Promise.all([
        fetchJson("/api/status"),
        fetchJson("/api/hermes/status"),
        fetchJson("/api/system"),
        fetchJson("/api/logs/sources"),
        fetchJson("/api/logs/gateway_stdout?lines=50"),
        fetchJson("/api/logs/gateway_stderr?lines=50"),
      ]);

      renderService(service);
      renderHermes(hermes);
      renderSystem(system);
      renderLogsSummary(sources, stdout, stderr);
      renderLogPanel("stdout-meta", "log-stdout", "stdout-json", stdout);
      renderLogPanel("stderr-meta", "log-stderr", "stderr-json", stderr);

      document.getElementById("last-updated").textContent =
        "Sist oppdatert: " + new Date().toLocaleString("no-NO");
    }

    document.getElementById("refresh-btn").addEventListener("click", loadDashboard);
    loadDashboard();
  </script>
</body>
</html>
"""


def render_dashboard() -> str:
    return DASHBOARD_HTML
