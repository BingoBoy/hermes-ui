# Phase 5: Verified Service Actions and Bob Interaction Planning - Context

**Gathered:** 2026-06-04
**Status:** Ready for planning
**Scope:** Plan safe service controls and Bob task entry — no runtime write actions in this discuss phase

<domain>

## Phase Boundary

Phase 5 plans the transition from read-only Hermes UI to a safe control panel where Truls can restart Hermes Gateway and eventually submit bounded tasks to Bob. This discuss phase produces verified command contracts, a security model, sub-phase breakdown (5A–5D), and an executable plan for the first safe slice (5A restart-only). It does not implement write routes or change LaunchAgent/Cloudflare configuration.

Two tracks:

- **Track A — Verified Service Actions:** Allowlisted `launchctl` controls for Hermes Gateway only (`ai.hermes.gateway`).
- **Track B — Bob Interaction Entry Point:** Map safe Hermes CLI entry points for submitting a bounded text task without a browser terminal.

</domain>

<decisions>

## Implementation Decisions

### Track A — Service Actions

- **D-01:** Service actions target **Hermes Gateway only** — label `ai.hermes.gateway`, plist `/Users/trulsdahl/Library/LaunchAgents/ai.hermes.gateway.plist`. Hermes UI (`no.truls.hermes-ui`) must never be controllable from the web UI (self-restart trap).
- **D-02:** Use **direct fixed `launchctl` argv lists** via `subprocess.run(..., shell=False)` — same pattern as `backend/status.py::_run_read_only`. Do **not** use `hermes gateway start|stop|restart` in v1 write paths (`--all` flag risk, extra CLI dependency).
- **D-03:** **5A ships restart-only first.** Start/stop deferred to 5B after bootstrap/bootout are verified against a stopped gateway.
- **D-04:** Write actions require **explicit UI confirmation** — modal with service name, action label, and a confirm button; optional typed token `RESTART` for 5A.
- **D-05:** All write actions append to an **append-only audit log** at `/Users/trulsdahl/.hermes-ui/logs/service-actions.log` (override via `HERMES_UI_AUDIT_LOG`). Each entry: ISO timestamp, action id, actor hint (`cloudflare-access`), result, safe error summary. No secrets, no full stderr dumps.
- **D-06:** API responses are **structured JSON** with fields: `action`, `success`, `message`, `service`, `launchd_label`, `checked_at`, `audit_id`. Errors use safe `detail` strings — no tracebacks.
- **D-07:** New env gate **`ALLOW_SERVICE_ACTIONS=false`** (default). Write routes return `403` when disabled. Independent of `ALLOW_UNSAFE_COMMANDS` (which stays `false`).
- **D-08:** Post-action status poll: after restart, backend re-runs existing read-only `get_hermes_status()` and returns updated `running`/`launchctl` block.

### Verified launchctl Commands (Bob, 2026-06-04)

| Action | Command | Verification |
|--------|---------|--------------|
| Status (list) | `launchctl list` → match `ai.hermes.gateway` | Already used in `backend/status.py` |
| Status (detail) | `launchctl print gui/$(id -u)/ai.hermes.gateway` | Verified via SSH — shows `state = running`, program args, log paths |
| Restart | `launchctl kickstart -k gui/$(id -u)/ai.hermes.gateway` | **Live verified** — PID changed (88059 → 53383), service returned to running |
| Start | `launchctl bootstrap gui/$(id -u) /Users/trulsdahl/Library/LaunchAgents/ai.hermes.gateway.plist` | Documented; **not live-tested** (requires stopped gateway) |
| Stop | `launchctl bootout gui/$(id -u) /Users/trulsdahl/Library/LaunchAgents/ai.hermes.gateway.plist` | Documented; **not live-tested** (would interrupt live gateway) |

Domain path format: `gui/501/ai.hermes.gateway` (uid 501 for `trulsdahl`).

Error handling:

- `launchctl` not found → `success: false`, `detail: launchctl unavailable`
- Non-zero exit → `success: false`, include truncated stderr (max 200 chars, redacted)
- Timeout (5s for write actions) → `success: false`, `detail: action timed out`
- Gateway still not running after restart + 3s poll → `success: true` with `warning: service not detected after restart`

### Track B — Bob Interaction Entry Point

- **D-09:** Hermes Gateway has **no dedicated HTTP listen port** for UI integration. Gateway runs as launchd process (`python -m hermes_cli.main gateway run --replace`) and handles messaging platforms (Telegram confirmed in config).
- **D-10:** **Primary recommended entry for 5C:** `hermes kanban create "<title>" --body "<body>" --json` — durable SQLite task board, bounded input, idempotency key support, async execution via kanban dispatcher. Hermes UI wraps this as a fixed argv call, not user shell.
- **D-11:** **Secondary option for synchronous one-shot (5C alt):** `hermes chat -q "<prompt>" -Q --max-turns 1` — programmatic single query. Higher risk (agent loop, tools). Requires strict input length cap, no `--yolo`, no `--accept-hooks` unless explicitly approved.
- **D-12:** **Not recommended for UI v1:** `hermes -z` (oneshot with auto-bypass approvals), `hermes send` (outbound messaging only), free `hermes chat` REPL, `hermes gateway` subcommands for task ingress.
- **D-13:** **Response/history for 5D (read-only):** `hermes kanban list --json`, `hermes kanban show <id> --json`, `hermes sessions list` — parsed and redacted server-side. No raw session DB exposure.
- **D-14:** Bob interaction input limits (planned): title max 200 chars, body max 4000 chars, alphanumeric idempotency key from UI UUID, no file paths from client, no model/provider override from client in v1.

### Sub-Phase Breakdown

| Sub-phase | Scope | Depends on |
|-----------|-------|------------|
| **5A** | Restart-only + audit + confirmation UX | Verified kickstart |
| **5B** | Start/stop actions | 5A + live bootstrap/bootout verification |
| **5C** | Bob task entry (kanban create) | 5A security model + kanban CLI verification |
| **5D** | Task status/history view (read-only) | 5C |

### Claude's Discretion

- Exact confirmation UX copy and whether typed `RESTART` is required vs. double-click confirm.
- Audit log JSON vs. JSONL format (prefer JSONL one-object-per-line).
- Cooldown between restart attempts (recommend 30s server-side).

</decisions>

<canonical_refs>

## Canonical References

### Service actions and deployment

- `docs/architecture/deployment.md` — LaunchAgent model, Hermes UI vs Gateway separation
- `docs/security/README.md` — write-action gates, audit requirements
- `docs/api/service-actions.md` — planned API contract for Track A
- `docs/notion/04 API-spesifikasjon 374811e3522c81b89dccf3d7b1b0ab4c.md` — original POST endpoint sketches
- `docs/notion/08 Dette trenger Truls å finne frem 374811e3522c8193a2a8dac18245eae5.md` — Bob paths and likely commands
- `.planning/PROJECT.md` — likely commands marked unverified until this phase
- `.planning/REQUIREMENTS.md` — ACT-01 through ACT-04

### Bob interaction

- `docs/api/bob-interaction.md` — planned entry points for Track B
- `docs/notion/Hermes UI for Bob – grafisk brukergrensesnitt via  374811e3522c8159aaaad3eb9e89a568.md` — `/run-approved-task` vision

### Existing code patterns

- `backend/status.py` — `_run_read_only`, `_launchctl_status`, `get_hermes_status`
- `backend/config.py` — settings/env loading
- `backend/redaction.py` — reuse for audit log and CLI output sanitization
- `tests/test_api.py` — `test_no_write_action_routes_exist` guard

</canonical_refs>

<code_context>

## Existing Code Insights

### Reusable Assets

- `_run_read_only()` in `backend/status.py` — template for `_run_allowlisted_action()` with longer timeout and audit hook.
- `Settings.hermes_launchd_label` — already defaults to `ai.hermes.gateway`.
- `backend/redaction.py` — sanitize launchctl stderr and kanban output before API response.
- Dashboard gateway card in `backend/dashboard.py` — natural placement for restart button in 5A.

### Established Patterns

- Fixed argv subprocess, no shell, no client-supplied commands.
- Structured JSON everywhere; fail-safe degradation on inspection failures.
- Server-side allowlists (`log_sources.py` pattern) — apply same pattern to `service_actions.py` action registry.
- Tests assert no write routes exist — extend when 5A adds POST routes behind feature flag.

### Integration Points

- New module: `backend/service_actions.py` (allowlist + audit + launchctl runner).
- New routes in `backend/main.py`: `POST /api/hermes/restart` (5A only).
- Config: `ALLOW_SERVICE_ACTIONS`, `HERMES_LAUNCHD_PLIST`, `HERMES_UI_AUDIT_LOG`.
- Dashboard JS: confirmation modal before POST.

</code_context>

<specifics>

## Specific Ideas

- Truls wants Hermes UI to become a safe entry point for using Bob, not just viewing status.
- Cloudflare Access (`Only Truls`) remains the outer auth layer — no in-app token auth for MVP write actions.
- First executable slice: **restart gateway only** — lowest blast radius, already live-verified on Bob.

</specifics>

<deferred>

## Deferred Ideas

- Full chat UI — own phase after 5D.
- Browser terminal — permanently out of scope.
- Controlling Hermes UI LaunchAgent from dashboard — rejected (self-restart risk).
- `hermes gateway restart --all` — rejected (cross-profile kill risk).
- LM Studio / n8n / Docker controls — Phase 6 operations enrichment.
- In-app API token auth — defer; Cloudflare Access sufficient for single-user MVP.

</deferred>

---

*Phase: 5-Verified Service Actions and Bob Interaction Planning*
*Context gathered: 2026-06-04*
