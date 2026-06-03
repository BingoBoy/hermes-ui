# Phase 2: Verified Logs Viewer - Context

**Gathered:** 2026-06-03
**Status:** Ready for planning
**Scope:** Pre-implementation only - verify log paths and redaction rules

<domain>

## Phase Boundary

Phase 2 prepares a future bounded read-only log viewer. This phase verifies Hermes log paths on Bob, defines an allowlist model, defines redaction rules, and documents the implementation plan. It does not implement a log viewer, does not add API routes, does not read arbitrary files from browser input, and does not expose log contents.

</domain>

<decisions>

## Implementation Decisions

### Verified Bob/Hermes Facts

- **D-01:** Bob identity verified via `BobRemote`: hostname `Truls-sin-Mac-mini.local`, user `trulsdahl`.
- **D-02:** Hermes LaunchAgent plist verified at `/Users/trulsdahl/Library/LaunchAgents/ai.hermes.gateway.plist`.
- **D-03:** LaunchAgent label verified as `ai.hermes.gateway`.
- **D-04:** LaunchAgent working directory verified as `/Users/trulsdahl/.hermes/hermes-agent`.
- **D-05:** LaunchAgent program arguments verified as `/Users/trulsdahl/.hermes/hermes-agent/venv/bin/python -m hermes_cli.main gateway run --replace`.

### Verified Log Paths

- **D-06:** `StandardOutPath` is verified as `/Users/trulsdahl/.hermes/logs/gateway.log`.
- **D-07:** `StandardErrorPath` is verified as `/Users/trulsdahl/.hermes/logs/gateway.error.log`.
- **D-08:** Additional Hermes log files were discovered under `/Users/trulsdahl/.hermes/logs/`, but only explicit allowlisted files may be exposed later.

### Allowlist Model

- **D-09:** A future log viewer must use static server-side log source IDs, never paths from client input.
- **D-10:** Each source must define `log_id`, `display_name`, `absolute_path`, `max_lines`, `requires_redaction`, and `phase_status`.
- **D-11:** Allowed line limits must be bounded. Default should be 100 lines, maximum 500 lines.
- **D-12:** Backend/Hermes UI logs are TBD because Phase 1 runs Uvicorn interactively and does not yet write an application log file.

### Redaction Model

- **D-13:** All log output must pass redaction before response serialization or UI rendering.
- **D-14:** Redaction must cover tokens, API keys, Bearer headers, private key blocks, password fields, Cloudflare credentials, and `.env`-style lines.
- **D-15:** If redaction confidence is uncertain, fail closed by suppressing the affected line or returning a safe error.

### Safety Boundaries

- **D-16:** No log endpoint may accept an absolute path, relative path, glob, or arbitrary file name from the browser.
- **D-17:** No write actions, start/stop/restart controls, free terminal, or shell-command route may be added while planning logs.
- **D-18:** Future implementation must read from allowlisted files only and should handle missing files safely.

</decisions>

<specifics>

## Specific Ideas

- Use human-friendly log names in the UI such as "Hermes gateway output" and "Hermes gateway errors".
- Keep metadata about discovered but not yet exposed logs so future planning can decide deliberately.
- Do not expose `.hermes_history`, `.git/logs`, source files, tests, or virtualenv files even if they appear in broad filesystem scans.

</specifics>

<canonical_refs>

## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project State

- `.planning/STATE.md` - Current project memory and open gates.
- `.planning/ROADMAP.md` - Phase 2 scope and success criteria.
- `.planning/REQUIREMENTS.md` - Deferred log requirements `LOGS-01` through `LOGS-03`.
- `docs/security/README.md` - Security boundaries and gates.

### Current Code

- `backend/main.py` - Current API route surface; no log route exists yet.
- `backend/status.py` - Existing read-only inspection pattern using fixed commands without `shell=True`.
- `tests/test_api.py` - Existing tests that assert no write-action routes exist.

### Source Context

- `docs/notion/04 API-spesifikasjon 374811e3522c81b89dccf3d7b1b0ab4c.md` - Original log endpoint idea; must be constrained by this context.
- `docs/notion/08 Dette trenger Truls å finne frem 374811e3522c8193a2a8dac18245eae5.md` - Bob/Hermes setup and previously unknown log path status.

</canonical_refs>

<code_context>

## Existing Code Insights

### Reusable Assets

- `backend/status.py` demonstrates fixed, read-only local inspection with `subprocess.run(..., shell=False)`.
- `backend/config.py` centralizes safe defaults and should later hold log source defaults or a helper for loading them.
- `tests/test_api.py` already guards against write-action routes and should be extended when log routes are implemented.

### Established Patterns

- API endpoints are explicit and small.
- Current routes are GET-only.
- Missing local services should return safe structured responses rather than raising raw errors.

### Integration Points

- Future log route should likely be `GET /api/logs/{log_id}?lines=100`, where `log_id` maps to a server-side allowlist entry.
- Dashboard should later show log snippets only from allowlisted sources and only after redaction.

</code_context>

<deferred>

## Deferred Ideas

- Implementing `GET /api/logs/{log_id}` - future execution after this plan is approved.
- Rendering log snippets in the dashboard - future execution.
- Adding backend persistent log files for Hermes UI itself - needs a separate runtime/deployment decision.
- Start/stop/restart and audit logging - Phase 3.

</deferred>

---

*Phase: 02-verified-logs-viewer*
*Context gathered: 2026-06-03*
