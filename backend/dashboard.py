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
    button.danger {
      border-color: #fecaca;
      background: #fef2f2;
      color: #b91c1c;
    }
    button.danger:hover { background: #fee2e2; }
    button:disabled {
      opacity: 0.55;
      cursor: not-allowed;
    }
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
    .action-row {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-top: 12px;
      align-items: center;
    }
    .action-result {
      margin-top: 10px;
      font-size: 0.9rem;
      padding: 10px 12px;
      border-radius: 10px;
      display: none;
    }
    .action-result.ok {
      display: block;
      background: var(--ok-bg);
      color: var(--ok);
    }
    .action-result.bad {
      display: block;
      background: var(--bad-bg);
      color: var(--bad);
    }
    .action-result.warn {
      display: block;
      background: var(--warn-bg);
      color: var(--warn);
    }
    .modal-backdrop {
      position: fixed;
      inset: 0;
      background: rgba(15, 23, 42, 0.45);
      display: none;
      align-items: center;
      justify-content: center;
      padding: 24px;
      z-index: 20;
    }
    .modal-backdrop.open { display: flex; }
    .modal {
      width: min(100%, 420px);
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 20px;
      box-shadow: 0 20px 40px rgba(15, 23, 42, 0.18);
    }
    .modal h3 { margin: 0 0 8px; }
    .modal p { margin: 0 0 16px; color: var(--muted); line-height: 1.5; }
    .modal-actions {
      display: flex;
      justify-content: flex-end;
      gap: 10px;
      flex-wrap: wrap;
    }
    .bob-section {
      margin-top: 20px;
    }
    .bob-section h2 {
      margin: 0 0 8px;
      font-size: 1.15rem;
    }
    .bob-intro {
      color: var(--muted);
      font-size: 0.92rem;
      margin: 0 0 14px;
      line-height: 1.5;
    }
    .bob-task-templates {
      margin-bottom: 18px;
      max-width: 640px;
    }
    .bob-task-templates h3 {
      margin: 0 0 6px;
      font-size: 1rem;
    }
    .bob-template-intro {
      margin-bottom: 10px;
    }
    .bob-template-list {
      display: grid;
      gap: 14px;
    }
    .bob-template-item {
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 12px 14px;
      background: var(--card);
    }
    .bob-template-item h4 {
      margin: 0 0 8px;
      font-size: 0.95rem;
    }
    .bob-template-item .field {
      margin-bottom: 10px;
    }
    .bob-template-send-btn {
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 8px 14px;
      font: inherit;
      background: #f8fafc;
      cursor: pointer;
    }
    .bob-template-send-btn:hover:not(:disabled) {
      border-color: #94a3b8;
      background: #fff;
    }
    .bob-template-send-btn:disabled,
    .bob-template-input:disabled {
      opacity: 0.65;
      cursor: not-allowed;
    }
    .bob-form {
      display: grid;
      gap: 12px;
      max-width: 640px;
    }
    .field label {
      display: block;
      font-size: 0.78rem;
      text-transform: uppercase;
      letter-spacing: 0.03em;
      color: var(--muted);
      margin-bottom: 4px;
    }
    .field input,
    .field textarea {
      width: 100%;
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 10px 12px;
      font: inherit;
      background: var(--card);
    }
    .field textarea {
      min-height: 120px;
      resize: vertical;
    }
    .bob-disabled {
      border-left: 4px solid var(--border);
      background: #f8fafc;
      padding: 12px 14px;
      border-radius: 12px;
      color: var(--muted);
      font-size: 0.92rem;
    }
    .bob-history-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 0.88rem;
      margin-top: 8px;
    }
    .bob-history-table th,
    .bob-history-table td {
      text-align: left;
      padding: 8px 6px;
      border-bottom: 1px solid var(--border);
      vertical-align: top;
    }
    .bob-history-table th {
      color: var(--muted);
      font-size: 0.75rem;
      text-transform: uppercase;
      letter-spacing: 0.03em;
    }
    .bob-history-table button.linkish {
      border: none;
      background: none;
      color: #2563eb;
      padding: 0;
      text-decoration: underline;
      cursor: pointer;
      font: inherit;
    }
    .bob-history-empty {
      color: var(--muted);
      font-style: italic;
      margin: 8px 0 0;
    }
    .bob-detail-panel {
      margin-top: 16px;
      padding-top: 14px;
      border-top: 1px solid var(--border);
    }
    .bob-detail-panel h3 {
      margin: 0 0 10px;
      font-size: 1rem;
    }
    .status-pill {
      display: inline-block;
      border-radius: 999px;
      padding: 2px 8px;
      font-size: 0.8rem;
      font-weight: 600;
      background: #eef2f7;
      color: var(--muted);
    }
    .status-pill.running { background: #dbeafe; color: #1d4ed8; }
    .status-pill.ready { background: var(--warn-bg); color: var(--warn); }
    .status-pill.completed,
    .status-pill.done { background: var(--ok-bg); color: var(--ok); }
    .status-pill.failed,
    .status-pill.blocked { background: var(--bad-bg); color: var(--bad); }
    .status-pill.unknown { background: #eef2f7; color: var(--muted); }
    .bob-toolbar-row {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      align-items: center;
      margin-bottom: 8px;
    }
    .bob-auto-refresh {
      font-size: 0.9rem;
      color: var(--muted);
      display: inline-flex;
      align-items: center;
      gap: 6px;
      cursor: pointer;
      user-select: none;
    }
    .bob-row-highlight td { background: #eff6ff; }
    .bob-result-flag {
      font-size: 0.75rem;
      font-weight: 600;
      color: var(--ok);
    }
    .bob-result-block {
      background: #f8fafc;
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 10px 12px;
      margin-top: 10px;
      white-space: pre-wrap;
      word-break: break-word;
      font-size: 0.88rem;
      line-height: 1.45;
      max-height: 280px;
      overflow: auto;
    }
    .bob-inbox-list {
      display: grid;
      gap: 10px;
      margin-top: 8px;
    }
    .bob-inbox-item {
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 12px 14px;
      background: #fafbfc;
    }
    .bob-inbox-item header {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 8px;
      margin-bottom: 6px;
    }
    .bob-inbox-item h4 {
      margin: 0;
      font-size: 0.95rem;
      flex: 1 1 160px;
    }
    .bob-inbox-excerpt {
      color: var(--muted);
      font-size: 0.88rem;
      margin: 0 0 8px;
      line-height: 1.45;
      white-space: pre-wrap;
      word-break: break-word;
    }
    .bob-inbox-excerpt.bob-result-collapsed {
      max-height: 4.5em;
      overflow: hidden;
    }
    .bob-inbox-meta {
      font-size: 0.82rem;
      color: var(--muted);
      margin: 0 0 6px;
    }
    .bob-inbox-actions,
    .bob-result-toolbar {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;
      margin-top: 4px;
    }
    .bob-copy-btn {
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 5px 10px;
      font-size: 0.82rem;
      background: var(--card);
      cursor: pointer;
    }
    .bob-copy-btn:hover:not(:disabled) {
      border-color: #94a3b8;
      background: #f8fafc;
    }
    .bob-copy-btn:disabled {
      opacity: 0.7;
      cursor: default;
    }
    .bob-result-toggle {
      margin: 4px 0 0;
      padding: 0;
    }
    .bob-result-block.bob-result-collapsed {
      max-height: 140px;
      overflow: hidden;
    }
    .ops-section {
      margin-top: 20px;
    }
    .ops-section h2 {
      margin: 0 0 8px;
      font-size: 1.15rem;
    }
    .ops-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      gap: 16px;
      margin-top: 12px;
    }
    .ops-agent h3 {
      margin: 0 0 8px;
      font-size: 1rem;
    }
    .ops-docker {
      margin-top: 14px;
      padding-top: 12px;
      border-top: 1px solid var(--border);
      font-size: 0.9rem;
      color: var(--muted);
    }
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

    <section class="card bob-section" id="bob-inbox-section" aria-label="Bob Inbox">
      <h2>Bob Inbox</h2>
      <p class="bob-intro">
        Read-only innboks med ferdige oppgaver og resultater fra Bob (maks 8 nyeste).
      </p>
      <div class="bob-disabled" id="bob-inbox-disabled" hidden>
        Bob Inbox er deaktivert (<code>ALLOW_BOB_TASKS=false</code>).
      </div>
      <div id="bob-inbox-content" hidden>
        <div id="bob-inbox-list-wrap"></div>
      </div>
    </section>

    <section class="card bob-section" id="bob-task-section" aria-label="Send oppgave til Bob">
      <h2>Send oppgave til Bob</h2>
      <p class="bob-intro" id="bob-task-intro">
        Oppretter en asynkron kanban-oppgave på Bob — ikke live chat og ikke terminal.
      </p>
      <div class="bob-disabled" id="bob-task-disabled" hidden>
        Bob-oppgaver er deaktivert på denne serveren (<code>ALLOW_BOB_TASKS=false</code>).
      </div>
      <div id="bob-task-templates" class="bob-task-templates" hidden>
        <h3>Bob task-maler</h3>
        <p class="bob-intro bob-template-intro">
          Fyll eventuelt inn felter under og send mal til Bob — samme asynkrone kanban-flyt som skjemaet under.
        </p>
        <div id="bob-template-list" class="bob-template-list">
          <div class="bob-template-item" data-template-id="morgenbrief">
            <h4>Morgenbrief</h4>
            <div class="field">
              <label for="bob-template-input-morgenbrief">Fokus for dagen</label>
              <input type="text" class="bob-template-input" id="bob-template-input-morgenbrief"
                maxlength="300" placeholder="Valgfritt fokus" autocomplete="off" />
            </div>
            <button type="button" class="bob-template-send-btn" data-template-id="morgenbrief">Send mal til Bob</button>
          </div>
          <div class="bob-template-item" data-template-id="ukesrapport">
            <h4>Ukesrapport</h4>
            <div class="field">
              <label for="bob-template-input-ukesrapport">Periode</label>
              <input type="text" class="bob-template-input" id="bob-template-input-ukesrapport"
                maxlength="300" placeholder="f.eks. uke 23 eller denne uken" autocomplete="off" />
            </div>
            <button type="button" class="bob-template-send-btn" data-template-id="ukesrapport">Send mal til Bob</button>
          </div>
          <div class="bob-template-item" data-template-id="konkurrentanalyse">
            <h4>Konkurrentanalyse</h4>
            <div class="field">
              <label for="bob-template-input-konkurrentanalyse">Konkurrent eller tema</label>
              <input type="text" class="bob-template-input" id="bob-template-input-konkurrentanalyse"
                maxlength="300" placeholder="Valgfritt fokus" autocomplete="off" />
            </div>
            <button type="button" class="bob-template-send-btn" data-template-id="konkurrentanalyse">Send mal til Bob</button>
          </div>
          <div class="bob-template-item" data-template-id="nettsideanalyse">
            <h4>Nettsideanalyse</h4>
            <div class="field">
              <label for="bob-template-input-nettsideanalyse">URL som skal analyseres</label>
              <input type="text" class="bob-template-input" id="bob-template-input-nettsideanalyse"
                maxlength="300" placeholder="https://…" autocomplete="off" />
            </div>
            <button type="button" class="bob-template-send-btn" data-template-id="nettsideanalyse">Send mal til Bob</button>
          </div>
          <div class="bob-template-item" data-template-id="markedsforing">
            <h4>Markedsføringsstatus</h4>
            <div class="field">
              <label for="bob-template-input-markedsforing">Fokusområde</label>
              <input type="text" class="bob-template-input" id="bob-template-input-markedsforing"
                maxlength="300" placeholder="Valgfritt fokus" autocomplete="off" />
            </div>
            <button type="button" class="bob-template-send-btn" data-template-id="markedsforing">Send mal til Bob</button>
          </div>
        </div>
      </div>
      <form class="bob-form" id="bob-task-form" hidden>
        <div class="field">
          <label for="bob-task-title">Tittel</label>
          <input type="text" id="bob-task-title" name="title" maxlength="200" required
            placeholder="Kort oppgavetittel" autocomplete="off" />
        </div>
        <div class="field">
          <label for="bob-task-body">Beskrivelse (valgfri)</label>
          <textarea id="bob-task-body" name="body" maxlength="4000"
            placeholder="Hva skal Bob gjøre?"></textarea>
        </div>
        <div class="action-row">
          <button type="submit" id="bob-task-submit">Send oppgave</button>
        </div>
      </form>
      <div class="action-result" id="bob-task-result" aria-live="polite"></div>
    </section>

    <section class="card bob-section" id="bob-history-section" aria-label="Bob-oppgaver">
      <h2>Bob-oppgaver</h2>
      <p class="bob-intro">
        Read-only oppfølging av kanban-oppgaver — status, tidsstempler og resultat.
      </p>
      <div class="bob-disabled" id="bob-history-disabled" hidden>
        Oppgaveliste er deaktivert (<code>ALLOW_BOB_TASKS=false</code>).
      </div>
      <div id="bob-history-content" hidden>
        <div class="bob-toolbar-row">
          <button type="button" id="bob-history-refresh">Oppdater oppgaver</button>
          <label class="bob-auto-refresh" for="bob-auto-refresh-toggle">
            <input type="checkbox" id="bob-auto-refresh-toggle" />
            Auto-oppdater oppgaver (12s)
          </label>
        </div>
        <p class="log-meta" id="bob-history-meta">Ingen data lastet ennå.</p>
        <div id="bob-history-list-wrap"></div>
        <div class="bob-detail-panel" id="bob-history-detail" hidden>
          <h3 id="bob-detail-title">Oppgavedetaljer</h3>
          <dl class="meta" id="bob-detail-meta"></dl>
          <div id="bob-detail-result-wrap" hidden>
            <p class="log-meta" style="margin: 10px 0 4px;">Resultat</p>
            <div class="bob-result-toolbar" id="bob-detail-result-toolbar"></div>
            <pre class="bob-result-block" id="bob-detail-result"></pre>
            <button type="button" class="linkish bob-result-toggle" id="bob-detail-result-toggle" hidden>
              Vis mer
            </button>
          </div>
          <div id="bob-detail-artifacts-wrap" hidden>
            <p class="log-meta" style="margin: 10px 0 4px;">Artifakter</p>
            <div id="bob-detail-artifacts"></div>
          </div>
          <details><summary>Teknisk JSON</summary><pre id="bob-detail-json"></pre></details>
        </div>
      </div>
      <div class="action-result" id="bob-history-result" aria-live="polite"></div>
    </section>

    <section class="card ops-section" id="operations-section" aria-label="Drift og tjenester">
      <h2>Drift og tjenester</h2>
      <p class="bob-intro">
        Read-only LaunchAgent-detaljer for Hermes UI og Hermes gateway (verifiserte plist-stier på serveren).
      </p>
      <div id="operations-agents-wrap" class="ops-grid"></div>
      <div id="operations-tunnel-wrap" class="ops-tunnel" hidden></div>
      <div id="operations-docker-wrap" class="ops-docker" hidden></div>
      <details style="margin-top: 12px;">
        <summary>Teknisk JSON</summary>
        <pre id="operations-json">Laster...</pre>
      </details>
    </section>

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
        <div class="action-row" id="hermes-actions" hidden>
          <button type="button" class="danger" id="restart-btn">Restart Gateway</button>
        </div>
        <div class="action-result" id="hermes-action-result" aria-live="polite"></div>
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

    <section class="notice" id="dashboard-notice">
      Read-only kontrollpanel. Restart er tilgjengelig bare når service actions er aktivert på serveren.
      Oppdater siden manuelt eller bruk knappen over for å hente ny status.
    </section>
  </main>

  <div class="modal-backdrop" id="restart-modal" hidden>
    <div class="modal" role="dialog" aria-modal="true" aria-labelledby="restart-modal-title">
      <h3 id="restart-modal-title">Restart Hermes Gateway?</h3>
      <p>
        Dette restarter LaunchAgent <strong>ai.hermes.gateway</strong>.
        Gateway-messaging kan avbrytes kort. Handlingen logges i audit-loggen.
      </p>
      <div class="modal-actions">
        <button type="button" id="restart-cancel-btn">Avbryt</button>
        <button type="button" class="danger" id="restart-confirm-btn">Bekreft restart</button>
      </div>
    </div>
  </div>
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

    async function fetchJson(path, options) {
      const response = await fetch(path, options);
      if (!response.ok) {
        let detail = response.statusText;
        let body = null;
        try {
          body = await response.json();
          detail = body.detail?.detail || body.detail?.error || JSON.stringify(body.detail || body);
        } catch (_) {}
        return { ok: false, error: detail, status: response.status, body };
      }
      return { ok: true, data: await response.json(), status: response.status };
    }

    let serviceActionsEnabled = false;
    let bobTasksEnabled = false;

    const BOB_TASK_TEMPLATES = [
      {
        id: "morgenbrief",
        label: "Morgenbrief",
        title: "Lag morgenbrief",
        body:
          "Lag en kort morgenbrief for Truls med prioriteringer, relevante oppgaver og anbefalt fokus for arbeidsdagen.",
      },
      {
        id: "ukesrapport",
        label: "Ukesrapport",
        title: "Lag ukesrapport",
        body:
          "Lag en ukesrapport for Truls med oppsummering av viktig arbeid, åpne punkter, risikoer og anbefalte neste steg.",
      },
      {
        id: "konkurrentanalyse",
        label: "Konkurrentanalyse",
        title: "Kjør konkurrentanalyse",
        body:
          "Kjør en konkurrentanalyse for Tirna med fokus på relevante fagskole- og kursaktører, tydelige funn, kilder og anbefalte tiltak.",
      },
      {
        id: "nettsideanalyse",
        label: "Nettsideanalyse",
        title: "Analyser nettside",
        body:
          "Analyser en nettside for Tirna med fokus på budskap, konvertering, SEO, brukerreise og konkrete forbedringsforslag. Be om URL dersom den ikke er oppgitt i oppgaven.",
      },
      {
        id: "markedsforing",
        label: "Markedsføringsstatus",
        title: "Lag status for markedsføring",
        body:
          "Lag en kort status for markedsføring med pågående aktiviteter, flaskehalser, prioriterte tiltak og forslag til hva Truls bør følge opp først.",
      },
    ];

    function trimBobTemplateInput(value) {
      return String(value == null ? "" : value).trim();
    }

    function buildBobTaskTemplatePayload(templateId, rawInput) {
      const template = BOB_TASK_TEMPLATES.find((item) => item.id === templateId);
      if (!template) {
        return null;
      }
      const input = trimBobTemplateInput(rawInput);
      let body = template.body;

      if (templateId === "morgenbrief" && input) {
        body = `${body}\n\nDagens fokus: ${input}`;
      } else if (templateId === "ukesrapport") {
        const period = input || "denne uken";
        body = `Lag en ukesrapport for Truls for ${period} med oppsummering av viktig arbeid, åpne punkter, risikoer og anbefalte neste steg.`;
      } else if (templateId === "konkurrentanalyse" && input) {
        body = `${body}\n\nKonkurrent eller tema: ${input}`;
      } else if (templateId === "nettsideanalyse" && input) {
        body = `${body}\n\nURL som skal analyseres: ${input}`;
      } else if (templateId === "markedsforing" && input) {
        body = `${body}\n\nFokusområde: ${input}`;
      }

      return { title: template.title, body };
    }

    function getBobTemplateInputValue(templateId) {
      const input = document.getElementById(`bob-template-input-${templateId}`);
      return input ? input.value : "";
    }
    let bobTasksCache = [];
    let bobHighlightTaskId = null;
    let bobHighlightTimer = null;
    let bobAutoRefreshTimer = null;
    let bobHistoryFailureCount = 0;
    const BOB_AUTO_REFRESH_MS = 12000;
    const BOB_INBOX_MAX_ITEMS = 8;
    const BOB_RESULT_PREVIEW_LEN = 120;

    function escapeHtml(text) {
      const div = document.createElement("div");
      div.textContent = text == null ? "" : String(text);
      return div.innerHTML;
    }

    function normalizeBobStatus(status) {
      const normalized = String(status || "").toLowerCase();
      if (normalized === "done" || normalized === "completed") {
        return "completed";
      }
      if (normalized === "ready") {
        return "ready";
      }
      if (normalized === "running") {
        return "running";
      }
      if (normalized === "failed" || normalized === "blocked") {
        return "failed";
      }
      return "unknown";
    }

    function statusDisplayLabel(status) {
      const normalized = normalizeBobStatus(status);
      if (normalized === "completed") {
        return "completed";
      }
      if (normalized === "unknown" && status) {
        return String(status);
      }
      return normalized;
    }

    function taskSortTimestamp(task) {
      return (
        Number(task.completed_at) ||
        Number(task.started_at) ||
        Number(task.created_at) ||
        0
      );
    }

    function taskResultValue(task) {
      if (task == null) {
        return null;
      }
      if (task.result !== null && task.result !== undefined) {
        return task.result;
      }
      return task.latest_summary || null;
    }

    function taskHasResult(task) {
      const value = taskResultValue(task);
      if (value === null || value === undefined) {
        return false;
      }
      if (typeof value === "string") {
        return value.trim().length > 0;
      }
      return true;
    }

    function formatResultValue(result) {
      if (result === null || result === undefined) {
        return null;
      }
      if (typeof result === "object") {
        return JSON.stringify(result, null, 2);
      }
      return String(result);
    }

    function resultExcerpt(task) {
      const formatted = formatResultValue(taskResultValue(task));
      if (!formatted) {
        return "";
      }
      const oneLine = formatted.replace(/\\s+/g, " ").trim();
      if (oneLine.length <= BOB_RESULT_PREVIEW_LEN) {
        return oneLine;
      }
      return oneLine.slice(0, BOB_RESULT_PREVIEW_LEN - 3) + "...";
    }

    function getTaskResultText(task) {
      return formatResultValue(taskResultValue(task)) || "";
    }

    async function copyTextToClipboard(text) {
      const value = String(text == null ? "" : text);
      if (!value) {
        return false;
      }
      try {
        if (navigator.clipboard && navigator.clipboard.writeText) {
          await navigator.clipboard.writeText(value);
          return true;
        }
      } catch (_) {}
      try {
        const textarea = document.createElement("textarea");
        textarea.value = value;
        textarea.setAttribute("readonly", "");
        textarea.style.position = "fixed";
        textarea.style.left = "-9999px";
        document.body.appendChild(textarea);
        textarea.select();
        const ok = document.execCommand("copy");
        document.body.removeChild(textarea);
        return ok;
      } catch (_) {
        return false;
      }
    }

    function flashBobCopyFeedback(button, ok) {
      const prev = button.textContent;
      button.textContent = ok ? "Kopiert" : "Kunne ikke kopiere";
      button.disabled = true;
      setTimeout(() => {
        button.textContent = prev;
        button.disabled = false;
      }, 1600);
    }

    function createBobCopyButton(label, getText) {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "bob-copy-btn";
      btn.textContent = label;
      btn.addEventListener("click", async () => {
        const ok = await copyTextToClipboard(getText());
        flashBobCopyFeedback(btn, ok);
      });
      return btn;
    }

    function appendBobCopyActions(container, task, actionsClass) {
      const useToolbarDirect =
        actionsClass === "bob-result-toolbar" &&
        container.classList &&
        container.classList.contains("bob-result-toolbar");
      const actions = useToolbarDirect
        ? container
        : document.createElement("div");
      if (!useToolbarDirect) {
        actions.className = actionsClass || "bob-inbox-actions";
      }
      const resultText = getTaskResultText(task);
      if (resultText) {
        actions.appendChild(
          createBobCopyButton("Kopier resultat", () => resultText)
        );
      }
      const taskId = task.id || "";
      if (taskId) {
        actions.appendChild(createBobCopyButton("Kopier ID", () => taskId));
      }
      const title = task.title || "";
      if (title) {
        actions.appendChild(createBobCopyButton("Kopier tittel", () => title));
      }
      if (!useToolbarDirect && actions.childElementCount) {
        container.appendChild(actions);
      }
    }

    function bindResultExpandToggle(toggleBtn, contentEl, fullText) {
      if (!fullText || fullText.length <= BOB_RESULT_PREVIEW_LEN) {
        toggleBtn.hidden = true;
        contentEl.classList.remove("bob-result-collapsed");
        contentEl.textContent = fullText || "";
        return;
      }
      const isPre = contentEl.tagName === "PRE";
      const compact = fullText.replace(/\\s+/g, " ").trim();
      const shortPreview =
        compact.length > BOB_RESULT_PREVIEW_LEN
          ? compact.slice(0, BOB_RESULT_PREVIEW_LEN - 3) + "..."
          : compact;
      let expanded = false;
      toggleBtn.hidden = false;
      if (isPre) {
        contentEl.textContent = fullText;
        contentEl.classList.add("bob-result-collapsed");
      } else {
        contentEl.textContent = shortPreview;
        contentEl.classList.add("bob-result-collapsed");
      }
      toggleBtn.textContent = "Vis mer";
      toggleBtn.onclick = () => {
        expanded = !expanded;
        if (expanded) {
          contentEl.classList.remove("bob-result-collapsed");
          if (!isPre) {
            contentEl.textContent = fullText;
          }
          toggleBtn.textContent = "Vis mindre";
        } else {
          contentEl.classList.add("bob-result-collapsed");
          if (!isPre) {
            contentEl.textContent = shortPreview;
          }
          toggleBtn.textContent = "Vis mer";
        }
      };
    }

    function renderBobTaskArtifacts(payload) {
      const wrap = document.getElementById("bob-detail-artifacts-wrap");
      const target = document.getElementById("bob-detail-artifacts");
      const artifacts = Array.isArray(payload.artifacts) ? payload.artifacts : [];
      target.innerHTML = "";
      if (!artifacts.length) {
        wrap.hidden = true;
        return;
      }
      wrap.hidden = false;
      for (const artifact of artifacts) {
        const item = document.createElement("div");
        item.className = "bob-artifact-item";
        const title = document.createElement("p");
        title.className = "log-meta";
        title.textContent = `${artifact.relative_path || "artifact"} (${artifact.size_bytes || 0} bytes)`;
        const actions = document.createElement("div");
        actions.className = "bob-result-toolbar";
        actions.appendChild(
          createBobCopyButton("Kopier artifakt", () => artifact.content || "")
        );
        const content = document.createElement("pre");
        content.className = "bob-result-block";
        content.textContent = artifact.content || "";
        item.appendChild(title);
        item.appendChild(actions);
        item.appendChild(content);
        target.appendChild(item);
      }
    }

    function inboxMetaLine(task) {
      const parts = [];
      if (task.id) {
        parts.push(task.id);
      }
      if (task.completed_at) {
        parts.push(`Fullført ${formatUnixTime(task.completed_at)}`);
      } else if (task.created_at) {
        parts.push(`Opprettet ${formatUnixTime(task.created_at)}`);
      }
      return parts.join(" · ");
    }

    function isInboxCandidate(task) {
      const status = normalizeBobStatus(task.status);
      if (status === "completed" || status === "failed") {
        return true;
      }
      return taskHasResult(task);
    }

    function setBobTaskResult(message, tone) {
      const target = document.getElementById("bob-task-result");
      target.textContent = message;
      target.className = "action-result " + tone;
    }

    function clearBobTaskResult() {
      const target = document.getElementById("bob-task-result");
      target.textContent = "";
      target.className = "action-result";
    }

    function stopBobAutoRefresh() {
      if (bobAutoRefreshTimer) {
        clearInterval(bobAutoRefreshTimer);
        bobAutoRefreshTimer = null;
      }
    }

    function startBobAutoRefresh() {
      stopBobAutoRefresh();
      const toggle = document.getElementById("bob-auto-refresh-toggle");
      if (!bobTasksEnabled || !toggle || !toggle.checked) {
        return;
      }
      bobAutoRefreshTimer = setInterval(() => {
        loadBobHistory({ silent: true });
      }, BOB_AUTO_REFRESH_MS);
    }

    function scheduleBobHighlight(taskId) {
      bobHighlightTaskId = taskId;
      if (bobHighlightTimer) {
        clearTimeout(bobHighlightTimer);
      }
      bobHighlightTimer = setTimeout(() => {
        bobHighlightTaskId = null;
        renderBobHistoryList(bobTasksCache);
      }, 8000);
    }

    function setBobTaskCreateControlsDisabled(disabled) {
      const submitBtn = document.getElementById("bob-task-submit");
      if (submitBtn) {
        submitBtn.disabled = disabled;
      }
      document.querySelectorAll(".bob-template-send-btn").forEach((btn) => {
        btn.disabled = disabled;
      });
      document.querySelectorAll(".bob-template-input").forEach((input) => {
        input.disabled = disabled;
      });
    }

    function updateBobTasksUi(enabled) {
      bobTasksEnabled = !!enabled;
      const form = document.getElementById("bob-task-form");
      const templates = document.getElementById("bob-task-templates");
      const disabled = document.getElementById("bob-task-disabled");
      const historyContent = document.getElementById("bob-history-content");
      const historyDisabled = document.getElementById("bob-history-disabled");
      const inboxContent = document.getElementById("bob-inbox-content");
      const inboxDisabled = document.getElementById("bob-inbox-disabled");
      form.hidden = !bobTasksEnabled;
      if (templates) {
        templates.hidden = !bobTasksEnabled;
      }
      disabled.hidden = bobTasksEnabled;
      historyContent.hidden = !bobTasksEnabled;
      historyDisabled.hidden = bobTasksEnabled;
      inboxContent.hidden = !bobTasksEnabled;
      inboxDisabled.hidden = bobTasksEnabled;
      if (bobTasksEnabled) {
        loadBobHistory();
        startBobAutoRefresh();
      } else {
        stopBobAutoRefresh();
        bobTasksCache = [];
        renderBobInbox([]);
      }
    }

    function formatUnixTime(value) {
      if (value === null || value === undefined || value === "") {
        return "—";
      }
      const numeric = Number(value);
      if (!Number.isFinite(numeric)) {
        return String(value);
      }
      const ms = numeric > 1e12 ? numeric : numeric * 1000;
      return new Date(ms).toLocaleString("no-NO");
    }

    function statusPillClass(status) {
      return normalizeBobStatus(status);
    }

    function assigneeDisplayLabel(task) {
      const assignee = task && typeof task.assignee === "string" ? task.assignee.trim() : "";
      if (assignee) {
        return assignee;
      }
      const status = normalizeBobStatus(task == null ? null : task.status);
      if (status === "ready") {
        return "Legacy unassigned";
      }
      return "Ikke tildelt";
    }

    function assigneePillClass(task) {
      const assignee = task && typeof task.assignee === "string" ? task.assignee.trim() : "";
      if (assignee) {
        return "ok";
      }
      const status = normalizeBobStatus(task == null ? null : task.status);
      return status === "ready" ? "warn" : "bad";
    }

    function setBobHistoryResult(message, tone) {
      const target = document.getElementById("bob-history-result");
      target.textContent = message;
      target.className = "action-result " + tone;
    }

    function clearBobHistoryResult() {
      const target = document.getElementById("bob-history-result");
      target.textContent = "";
      target.className = "action-result";
    }

    function renderBobHistoryList(tasks) {
      const wrap = document.getElementById("bob-history-list-wrap");
      wrap.innerHTML = "";
      if (!tasks.length) {
        const empty = document.createElement("p");
        empty.className = "bob-history-empty";
        empty.textContent =
          "Ingen oppgaver ennå. Send en oppgave til Bob for å starte.";
        wrap.appendChild(empty);
        return;
      }
      const sorted = [...tasks].sort(
        (a, b) => taskSortTimestamp(b) - taskSortTimestamp(a)
      );
      const table = document.createElement("table");
      table.className = "bob-history-table";
      table.innerHTML = `
        <thead>
          <tr>
            <th>ID</th>
            <th>Tittel</th>
            <th>Status</th>
            <th>Assignee</th>
            <th>Opprettet</th>
            <th>Startet</th>
            <th>Fullført</th>
            <th>Resultat</th>
            <th></th>
          </tr>
        </thead>
        <tbody></tbody>
      `;
      const body = table.querySelector("tbody");
      for (const task of sorted) {
        const row = document.createElement("tr");
        if (bobHighlightTaskId && task.id === bobHighlightTaskId) {
          row.className = "bob-row-highlight";
        }
        const statusLabel = statusDisplayLabel(task.status);
        const cells = [
          `<td><code>${escapeHtml(task.id || "—")}</code></td>`,
          `<td>${escapeHtml(task.title || "—")}</td>`,
          `<td><span class="status-pill ${statusPillClass(task.status)}">${escapeHtml(statusLabel)}</span></td>`,
          `<td><span class="badge ${assigneePillClass(task)}">${escapeHtml(assigneeDisplayLabel(task))}</span></td>`,
          `<td>${escapeHtml(formatUnixTime(task.created_at))}</td>`,
          `<td>${escapeHtml(formatUnixTime(task.started_at))}</td>`,
          `<td>${escapeHtml(formatUnixTime(task.completed_at))}</td>`,
          `<td>${taskHasResult(task) ? '<span class="bob-result-flag">Har resultat</span>' : "—"}</td>`,
          "<td></td>",
        ];
        row.innerHTML = cells.join("");
        const actionCell = row.lastElementChild;
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "linkish";
        btn.textContent = "Vis detaljer";
        btn.addEventListener("click", () => loadBobTaskDetail(task.id));
        actionCell.appendChild(btn);
        body.appendChild(row);
      }
      wrap.appendChild(table);
    }

    function renderBobInbox(tasks) {
      const wrap = document.getElementById("bob-inbox-list-wrap");
      wrap.innerHTML = "";
      const candidates = [...tasks]
        .filter(isInboxCandidate)
        .sort((a, b) => taskSortTimestamp(b) - taskSortTimestamp(a))
        .slice(0, BOB_INBOX_MAX_ITEMS);

      if (!candidates.length) {
        const empty = document.createElement("p");
        empty.className = "bob-history-empty";
        empty.textContent = "Ingen ferdige Bob-resultater ennå.";
        wrap.appendChild(empty);
        return;
      }

      const list = document.createElement("div");
      list.className = "bob-inbox-list";
      for (const task of candidates) {
        const card = document.createElement("article");
        card.className = "bob-inbox-item";
        const statusLabel = statusDisplayLabel(task.status);
        const excerpt = resultExcerpt(task);
        card.innerHTML = `
          <header>
            <h4>${escapeHtml(task.title || task.id || "Uten tittel")}</h4>
            <span class="status-pill ${statusPillClass(task.status)}">${escapeHtml(statusLabel)}</span>
          </header>
          <p class="bob-inbox-meta">${escapeHtml(inboxMetaLine(task))}</p>
        `;
        const resultText = getTaskResultText(task);
        if (resultText) {
          const excerptEl = document.createElement("p");
          excerptEl.className = "bob-inbox-excerpt";
          card.appendChild(excerptEl);
          const toggle = document.createElement("button");
          toggle.type = "button";
          toggle.className = "linkish bob-result-toggle";
          bindResultExpandToggle(toggle, excerptEl, resultText);
          card.appendChild(toggle);
        } else if (excerpt) {
          const excerptEl = document.createElement("p");
          excerptEl.className = "bob-inbox-excerpt";
          excerptEl.textContent = excerpt;
          card.appendChild(excerptEl);
        }
        appendBobCopyActions(card, task, "bob-inbox-actions");
        const actions = document.createElement("div");
        actions.className = "action-row";
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "linkish";
        btn.textContent = "Vis detaljer";
        btn.addEventListener("click", () => loadBobTaskDetail(task.id));
        actions.appendChild(btn);
        card.appendChild(actions);
        list.appendChild(card);
      }
      wrap.appendChild(list);
    }

    function renderBobTaskDetail(payload) {
      const panel = document.getElementById("bob-history-detail");
      const task = { ...(payload.task || {}) };
      if (
        (task.result === null || task.result === undefined || task.result === "") &&
        payload.latest_summary
      ) {
        task.latest_summary = payload.latest_summary;
      }
      panel.hidden = false;
      document.getElementById("bob-detail-title").textContent =
        task.title || payload.task_id || "Oppgavedetaljer";
      const rows = [
        ["Task ID", payload.task_id || task.id],
        ["Status", statusDisplayLabel(task.status)],
        ["Opprettet", formatUnixTime(task.created_at)],
        ["Startet", formatUnixTime(task.started_at)],
        ["Fullført", formatUnixTime(task.completed_at)],
      ];
      if (task.body) {
        rows.push(["Beskrivelse", task.body]);
      }
      rows.push(["Hendelser", String((payload.events || []).length)]);
      rows.push(["Kommentarer", String((payload.comments || []).length)]);
      setMeta("bob-detail-meta", rows);

      const resultWrap = document.getElementById("bob-detail-result-wrap");
      const resultBlock = document.getElementById("bob-detail-result");
      const resultToolbar = document.getElementById("bob-detail-result-toolbar");
      const resultToggle = document.getElementById("bob-detail-result-toggle");
      const formattedResult = getTaskResultText(task);
      if (formattedResult) {
        resultWrap.hidden = false;
        resultBlock.textContent = formattedResult;
        resultToolbar.innerHTML = "";
        appendBobCopyActions(resultToolbar, task, "bob-result-toolbar");
        bindResultExpandToggle(resultToggle, resultBlock, formattedResult);
      } else {
        resultWrap.hidden = true;
        resultBlock.textContent = "";
        resultToolbar.innerHTML = "";
        resultToggle.hidden = true;
      }
      renderBobTaskArtifacts(payload);
      setJson("bob-detail-json", payload);
    }

    async function loadBobTaskDetail(taskId) {
      if (!bobTasksEnabled || !taskId) {
        return;
      }
      clearBobHistoryResult();
      const result = await fetchJson(`/api/bob/tasks/${encodeURIComponent(taskId)}`);
      if (!result.ok) {
        setBobHistoryResult(result.error || "Kunne ikke hente detaljer", "bad");
        return;
      }
      renderBobTaskDetail(result.data);
      document.getElementById("bob-history-detail").scrollIntoView({ behavior: "smooth", block: "nearest" });
    }

    async function loadBobHistory(options) {
      if (!bobTasksEnabled) {
        return;
      }
      const silent = options && options.silent;
      const meta = document.getElementById("bob-history-meta");
      const refreshBtn = document.getElementById("bob-history-refresh");
      if (!silent) {
        refreshBtn.disabled = true;
        clearBobHistoryResult();
        meta.textContent = "Henter oppgaver...";
      }

      const result = await fetchJson("/api/bob/tasks?limit=50");
      if (!silent) {
        refreshBtn.disabled = false;
      }
      if (!result.ok) {
        bobHistoryFailureCount += 1;
        if (bobHistoryFailureCount >= 3) {
          stopBobAutoRefresh();
          const toggle = document.getElementById("bob-auto-refresh-toggle");
          if (toggle) {
            toggle.checked = false;
          }
        }
        meta.textContent = "Kunne ikke hente oppgaver";
        if (!silent) {
          setBobHistoryResult(
            result.error || "Kunne ikke hente oppgaver fra Bob. Prøv igjen senere.",
            "bad"
          );
        }
        return;
      }

      bobHistoryFailureCount = 0;
      const data = result.data;
      bobTasksCache = data.tasks || [];
      meta.textContent = `${data.count} oppgaver vist (maks 50) · sist sjekket ${formatUnixTime(data.checked_at)}`;
      renderBobHistoryList(bobTasksCache);
      renderBobInbox(bobTasksCache);
      if (!silent) {
        clearBobHistoryResult();
      }
    }

    async function submitBobTaskPayload({ title, body, clearForm, successLead }) {
      if (!bobTasksEnabled) {
        return { ok: false };
      }
      setBobTaskCreateControlsDisabled(true);
      clearBobTaskResult();

      const result = await fetchJson("/api/bob/tasks", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title, body }),
      });

      if (!result.ok) {
        setBobTaskResult(result.error || "Kunne ikke sende oppgave", "bad");
        setBobTaskCreateControlsDisabled(false);
        return result;
      }

      const data = result.data;
      const lead = successLead || "Oppgave opprettet.";
      setBobTaskResult(
        `${lead} task_id: ${data.task_id} · audit_id: ${data.audit_id}`,
        "ok"
      );
      if (clearForm) {
        const titleInput = document.getElementById("bob-task-title");
        const bodyInput = document.getElementById("bob-task-body");
        if (titleInput) {
          titleInput.value = "";
        }
        if (bodyInput) {
          bodyInput.value = "";
        }
      }
      setBobTaskCreateControlsDisabled(false);
      scheduleBobHighlight(data.task_id);
      await loadBobHistory();
      if (data.task_id) {
        await loadBobTaskDetail(data.task_id);
      }
      return result;
    }

    async function sendBobTaskTemplate(templateId) {
      const template = BOB_TASK_TEMPLATES.find((item) => item.id === templateId);
      if (!template || !bobTasksEnabled) {
        return;
      }
      const payload = buildBobTaskTemplatePayload(
        templateId,
        getBobTemplateInputValue(templateId)
      );
      if (!payload) {
        return;
      }
      const btn = document.querySelector(
        `.bob-template-send-btn[data-template-id="${templateId}"]`
      );
      const prevLabel = btn ? btn.textContent : "Send mal til Bob";
      if (btn) {
        btn.textContent = "Sender …";
      }
      await submitBobTaskPayload({
        title: payload.title,
        body: payload.body,
        clearForm: false,
        successLead: "Oppgave sendt til Bob.",
      });
      if (btn) {
        btn.textContent = prevLabel;
      }
    }

    async function submitBobTask(event) {
      event.preventDefault();
      if (!bobTasksEnabled) {
        return;
      }
      const titleInput = document.getElementById("bob-task-title");
      const bodyInput = document.getElementById("bob-task-body");
      await submitBobTaskPayload({
        title: titleInput.value,
        body: bodyInput.value,
        clearForm: true,
        successLead: "Oppgave opprettet.",
      });
    }

    function setActionResult(message, tone) {
      const target = document.getElementById("hermes-action-result");
      target.textContent = message;
      target.className = "action-result " + tone;
    }

    function clearActionResult() {
      const target = document.getElementById("hermes-action-result");
      target.textContent = "";
      target.className = "action-result";
    }

    function updateDashboardNotice() {
      const notice = document.getElementById("dashboard-notice");
      const parts = [];
      if (serviceActionsEnabled) {
        parts.push(
          "Gateway restart er aktivert (ALLOW_SERVICE_ACTIONS=true) og krever bekreftelse."
        );
      }
      if (bobTasksEnabled) {
        parts.push(
          "Bob-oppgaver er aktivert (ALLOW_BOB_TASKS=true) via kanban — ikke chat."
        );
      }
      if (!parts.length) {
        notice.textContent =
          "Read-only kontrollpanel. Write-actions krever ALLOW_SERVICE_ACTIONS eller ALLOW_BOB_TASKS på serveren.";
      } else {
        notice.textContent = parts.join(" ");
      }
    }

    function updateServiceActionsUi(enabled) {
      serviceActionsEnabled = !!enabled;
      const actions = document.getElementById("hermes-actions");
      actions.hidden = !serviceActionsEnabled;
      updateDashboardNotice();
    }

    function openRestartModal() {
      const modal = document.getElementById("restart-modal");
      modal.hidden = false;
      modal.classList.add("open");
    }

    function closeRestartModal() {
      const modal = document.getElementById("restart-modal");
      modal.classList.remove("open");
      modal.hidden = true;
    }

    async function confirmRestart() {
      const confirmBtn = document.getElementById("restart-confirm-btn");
      confirmBtn.disabled = true;
      clearActionResult();
      closeRestartModal();

      const result = await fetchJson("/api/hermes/restart", { method: "POST" });
      if (!result.ok) {
        const message = result.error || "Restart feilet";
        setActionResult(message, "bad");
        confirmBtn.disabled = false;
        return;
      }

      const data = result.data;
      if (data.warning) {
        setActionResult(`${data.message}. ${data.warning}`, "warn");
      } else {
        setActionResult(data.message || "Restart fullført", data.success ? "ok" : "bad");
      }

      await loadDashboard();
      confirmBtn.disabled = false;
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
        ["Service actions", data.allow_service_actions ? "Aktivert" : "Deaktivert"],
        ["Bob tasks", data.allow_bob_tasks ? "Aktivert" : "Deaktivert"],
        ["Sjekket", data.checked_at],
      ]);
      setJson("service-json", data);
      updateServiceActionsUi(data.allow_service_actions);
      updateBobTasksUi(data.allow_bob_tasks);
      updateDashboardNotice();
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

    function renderOperations(payload) {
      const wrap = document.getElementById("operations-agents-wrap");
      const tunnelWrap = document.getElementById("operations-tunnel-wrap");
      const dockerWrap = document.getElementById("operations-docker-wrap");
      wrap.innerHTML = "";
      tunnelWrap.hidden = true;
      tunnelWrap.innerHTML = "";
      dockerWrap.hidden = true;
      dockerWrap.textContent = "";

      if (!payload.ok) {
        wrap.innerHTML = `<p class="error-text">Kunne ikke hente driftstatus: ${escapeHtml(payload.error || "ukjent feil")}</p>`;
        setJson("operations-json", payload);
        return;
      }

      const data = payload.data;
      const agents = data.launch_agents || [];
      if (!agents.length) {
        wrap.innerHTML = '<p class="subtle">Ingen LaunchAgent-data tilgjengelig.</p>';
      }

      for (const agent of agents) {
        const card = document.createElement("article");
        card.className = "card ops-agent";
        const plist = agent.plist || {};
        const logs = plist.log_paths || {};
        const running = agent.running;
        const state = (agent.launchctl_print || {}).state || "—";
        const title = agent.id === "hermes-ui" ? "Hermes UI" : "Hermes Gateway";
        card.innerHTML = `
          <h3>${escapeHtml(title)}</h3>
          <div class="status-row">
            <span class="badge ${running ? "ok" : "warn"}">${running ? "Running" : "Not running"}</span>
            <span class="subtle">launchd: ${escapeHtml(state)}</span>
          </div>
          <dl class="meta">
            <dt>Label</dt><dd>${escapeHtml(agent.label || "—")}</dd>
            <dt>Plist</dt><dd>${escapeHtml(agent.plist_path || "—")}</dd>
            <dt>Program</dt><dd>${escapeHtml(plist.program_summary || "—")}</dd>
            <dt>Stdout-logg</dt><dd>${escapeHtml(logs.stdout || "—")}</dd>
            <dt>Stderr-logg</dt><dd>${escapeHtml(logs.stderr || "—")}</dd>
            <dt>Arbeidsmappe</dt><dd>${escapeHtml(plist.working_directory || "—")}</dd>
          </dl>
        `;
        wrap.appendChild(card);
      }

      const tunnel = data.cloudflare_tunnel || null;
      if (tunnel) {
        tunnelWrap.hidden = false;
        const cf = tunnel.cloudflared || {};
        const edge = tunnel.edge_probe || {};
        const processRunning = !!cf.process_running;
        const edgeStatus = edge.http_status != null ? String(edge.http_status) : "—";
        const accessRedirect = edge.access_redirect ? "Ja" : "Nei";
        const edgeNote = edge.enabled === false
          ? "Edge-probe deaktivert"
          : (edge.error ? escapeHtml(edge.error) : `HTTP ${edgeStatus}`);
        tunnelWrap.innerHTML = `
          <article class="card ops-agent">
            <h3>Cloudflare Tunnel</h3>
            <p class="subtle">${escapeHtml(tunnel.disclaimer || "Lokal observasjon — ikke full edge-status.")}</p>
            <div class="status-row">
              <span class="badge ${processRunning ? "ok" : "warn"}">${processRunning ? "cloudflared kjører" : "cloudflared ikke observert"}</span>
              <span class="subtle">Lokal agent observert</span>
            </div>
            <dl class="meta">
              <dt>Offentlig URL</dt><dd>${escapeHtml(tunnel.public_hostname || "—")}</dd>
              <dt>Tunnel-navn</dt><dd>${escapeHtml(tunnel.tunnel_name || "—")}</dd>
              <dt>Service target</dt><dd>${escapeHtml(tunnel.service_target || "—")}</dd>
              <dt>cloudflared</dt><dd>${escapeHtml(cf.version || (cf.installed ? "installert" : "ikke funnet"))}</dd>
              <dt>Edge-probe</dt><dd>${edgeNote}</dd>
              <dt>Access-viderekobling</dt><dd>${accessRedirect}</dd>
            </dl>
          </article>
        `;
      }

      const docker = data.docker || {};
      if (docker.included) {
        dockerWrap.hidden = false;
        if (!docker.available) {
          dockerWrap.textContent = `Docker: ${docker.detail || "utilgjengelig"}`;
        } else {
          const names = (docker.containers || []).join(", ") || "ingen containere";
          dockerWrap.textContent =
            `Docker ${docker.server_version || ""}: ${docker.container_count || 0} container(e) — ${names}`;
        }
      } else {
        dockerWrap.hidden = false;
        dockerWrap.textContent =
          "Docker-status er deaktivert (HERMES_OPS_INCLUDE_DOCKER=false). Gateway kjører via LaunchAgent.";
      }

      setJson("operations-json", data);
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
      const [service, hermes, system, operations, sources, stdout, stderr] = await Promise.all([
        fetchJson("/api/status"),
        fetchJson("/api/hermes/status"),
        fetchJson("/api/system"),
        fetchJson("/api/operations"),
        fetchJson("/api/logs/sources"),
        fetchJson("/api/logs/gateway_stdout?lines=50"),
        fetchJson("/api/logs/gateway_stderr?lines=50"),
      ]);

      renderService(service);
      renderHermes(hermes);
      renderSystem(system);
      renderOperations(operations);
      renderLogsSummary(sources, stdout, stderr);
      renderLogPanel("stdout-meta", "log-stdout", "stdout-json", stdout);
      renderLogPanel("stderr-meta", "log-stderr", "stderr-json", stderr);

      document.getElementById("last-updated").textContent =
        "Sist oppdatert: " + new Date().toLocaleString("no-NO");
    }

    document.getElementById("refresh-btn").addEventListener("click", loadDashboard);
    document.getElementById("restart-btn").addEventListener("click", openRestartModal);
    document.getElementById("restart-cancel-btn").addEventListener("click", closeRestartModal);
    document.getElementById("restart-confirm-btn").addEventListener("click", confirmRestart);
    document.getElementById("restart-modal").addEventListener("click", (event) => {
      if (event.target.id === "restart-modal") {
        closeRestartModal();
      }
    });
    document.getElementById("bob-task-form").addEventListener("submit", submitBobTask);
    document.querySelectorAll(".bob-template-send-btn").forEach((btn) => {
      btn.addEventListener("click", () => sendBobTaskTemplate(btn.dataset.templateId));
    });
    document.getElementById("bob-history-refresh").addEventListener("click", () => {
      loadBobHistory();
    });
    document.getElementById("bob-auto-refresh-toggle").addEventListener("change", () => {
      startBobAutoRefresh();
    });
    loadDashboard();
  </script>
</body>
</html>
"""


def render_dashboard() -> str:
    return DASHBOARD_HTML
