# Phase 5C: Bob Task Entry via Hermes Kanban - Context

**Gathered:** 2026-06-04
**Status:** Ready for planning
**Scope:** Plan safe Bob task creation from Hermes UI via `hermes kanban create` — no runtime implementation in this discuss phase

<domain>

## Phase Boundary

Phase 5C delivers a bounded write path for Truls to submit an asynchronous task to Bob from the Access-protected Hermes UI dashboard. The backend invokes only a fixed `hermes kanban create` argv list (no shell, no client flags, no chat, no terminal). Read-only task history (`kanban list` / `show`) belongs to Phase 5D.

Out of scope for 5C: chat UI, browser terminal, `hermes -z`, `hermes send`, gateway start/stop, LaunchAgent/Cloudflare changes, arbitrary CLI flags from the client.

</domain>

<decisions>

## Implementation Decisions

### Hermes kanban CLI contract (verified locally 2026-06-04; Bob path documented)

- **D-01:** Hermes binary on Bob (documented): `/Users/trulsdahl/.hermes/hermes-agent/venv/bin/hermes`. Override via env `HERMES_CLI_BIN` in Hermes UI settings at execute time. Do not accept binary path from API client.
- **D-02:** **Create argv (fixed, allowlisted action `create_kanban_task` only):**
  ```text
  [HERMES_CLI_BIN, "kanban", "create", <title>, "--body", <body>, "--idempotency-key", <server_uuid>, "--json"]
  ```
  Omit `--body` and its value when body is empty after normalization. Never pass client-supplied flags (`--skill`, `--assignee`, `--triage`, `--yolo`, etc.).
- **D-03:** **Create success JSON (stdout, exit 0):** single object with at least `id` (e.g. `t_06aa482f`), `title`, `body`, `status` (e.g. `ready`), `created_at` (unix int). Map `id` → API `task_id`.
- **D-04:** **Create duplicate idempotency:** same `--idempotency-key` returns existing task JSON with exit 0 — server generates UUID per submit attempt; retries with same server key on network failure are safe.
- **D-05:** **Create CLI errors:** missing title → argparse message on stderr, exit **2**. Backend treats non-zero exit or unparseable stdout as failure with safe `detail`.
- **D-06:** **List (5D only, documented now):** `hermes kanban list --json` → JSON **array** of task objects (same field shape as create). Optional `limit` enforced server-side by slicing parsed array, not client CLI flags beyond fixed `--json`.
- **D-07:** **Show (5D only):** `hermes kanban show <task_id> --json` → object with `task`, `comments`, `events`, `runs`, etc. **Quirk:** missing task prints `no such task: <id>` (often stderr) with exit **0** — parser must detect message/empty `task`, not rely on exit code alone.
- **D-08:** **Subprocess:** `subprocess.run(..., shell=False)`, timeout **30s** for kanban create (longer than launchctl 5s). Reuse `backend/redaction.py` on stderr snippets in API errors.
- **D-09:** **Not used:** `hermes -z`, `hermes chat`, `hermes send`, `hermes gateway` for task ingress, `shell=True`, client command strings.

### Security model

- **D-10:** New gate **`ALLOW_BOB_TASKS=false`** (default), independent of `ALLOW_SERVICE_ACTIONS`. Disabled → HTTP **403** with safe JSON body.
- **D-11:** Allowlisted actions frozenset: `{create_kanban_task}` only for 5C write path.
- **D-12:** Input limits: `title` required, max **200** chars, no newlines (reject `\n`/`\r` with 400); `body` optional, max **4000** chars, plain text. Trim leading/trailing whitespace; collapse internal runs of spaces in title optional (trim only for v1).
- **D-13:** Audit log path: `/Users/trulsdahl/.hermes-ui/logs/bob-interactions.log` (JSONL), override `HERMES_UI_BOB_AUDIT_LOG`. Fields: `timestamp`, `audit_id`, `action`, `task_id`, `title_hash` (sha256), `body_length`, `success`, `exit_code`, `detail` (sanitized, max 200). Do **not** log full body.
- **D-14:** Cooldown **60s** between successful task creates per process (separate from restart 30s). Active cooldown → HTTP **429** with `retry_after` seconds.
- **D-15:** Never restart or control `no.truls.hermes-ui` or accept plist/label/path from client.

### API (5C execute)

- **D-16:** `POST /api/bob/tasks` with JSON body `{ "title": string, "body": string? }`.
- **D-17:** Success **202** with `{ "success": true, "task_id", "status", "title", "submitted_at", "audit_id" }`. Errors: **400** validation, **403** gate, **429** cooldown, **502** CLI failure (safe detail).
- **D-18:** No `GET` task routes in 5C (defer to 5D).

### UI (5C execute)

- **D-19:** New dashboard section **«Send oppgave til Bob»** below gateway card: title input, body textarea, short copy that this creates an **async kanban task**, not live chat; submit button; success shows `task_id` + `audit_id`; error shows safe message from API.
- **D-20:** No confirmation modal required (lower blast radius than gateway restart); disable submit while in-flight.

### Bob live verification gate

- **D-21:** Local Mac CLI contract verified 2026-06-04. **Truls must re-run the same commands on Bob** before execute merge/deploy (path, JSON shape, dispatcher picks up `ready` tasks). See `05C-PLAN.md` verification section.

### Claude's Discretion

- Exact cooldown seconds (60s recommended).
- Whether to hide task form when `ALLOW_BOB_TASKS=false` vs show disabled state with explanation (prefer hidden/disabled + API 403 on direct POST).

</decisions>

<canonical_refs>

## Canonical References

### Bob task entry and security

- `docs/api/bob-interaction.md` — API contract, kanban CLI tables, verification commands
- `docs/security/README.md` — `ALLOW_BOB_TASKS` gate and audit rules
- `docs/architecture/deployment.md` — env vars on Bob, Hermes CLI path
- `.planning/phases/05-verified-service-actions/05-CONTEXT.md` — D-10–D-14 Bob entry decisions (parent phase)

### Patterns to mirror at execute

- `backend/service_actions.py` — allowlist, audit JSONL, cooldown, `shell=False`
- `backend/config.py` — env bool gates
- `backend/redaction.py` — stderr/CLI output sanitization
- `backend/dashboard.py` — restart section UX pattern
- `tests/test_service_actions.py` — security boundary tests

</canonical_refs>

<code_context>

## Existing Code Insights

### Reusable Assets

- `service_actions.py`: `_default_runner`, `write_audit_entry`, `_sanitize_detail`, `_make_audit_id`, cooldown exception pattern.
- `config.py`: add `allow_bob_tasks`, `hermes_cli_bin`, `bob_audit_log_path` at execute.
- `main.py`: register POST route with same error mapping as restart (403/429/502).

### Established Patterns

- Feature gates default false; fail closed.
- Fixed argv subprocess only; tests assert no `shell=True` in module source.

### Integration Points

- New module `backend/bob_tasks.py` called from `POST /api/bob/tasks` in `backend/main.py`.
- Dashboard HTML/JS section alongside existing restart modal block.

</code_context>

<specifics>

## Specific Ideas

- Production URL: `https://hermes-ui.strategistudio.no` (Cloudflare Access).
- 5A restart already live on Bob with `ALLOW_SERVICE_ACTIONS=true`; 5C must not alter that plist.
- User-facing copy in Norwegian on dashboard; API field names in English.

</specifics>

<deferred>

## Deferred Ideas

- **5D:** `GET /api/bob/tasks` and `GET /api/bob/tasks/{id}` via `kanban list/show --json`.
- **5C-b (optional):** synchronous `hermes chat -q` — explicitly rejected for 5C.
- **Chat UI / streaming** — future phase if ever.
- **Client-supplied idempotency key** — server-generated only in v1.

</deferred>

---

*Phase: 5C-Bob Task Entry via Hermes Kanban*
*Context gathered: 2026-06-04*
