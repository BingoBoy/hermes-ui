# State: Hermes UI for Bob

## Project Reference

See: `.planning/PROJECT.md` (updated 2026-06-03)

**Core value:** Truls can safely see whether Bob and Hermes are healthy without exposing shell access, secrets, or unsafe service controls.

**Current focus:** Phase 2 - Verified Logs Viewer

## Workflow

Use original GSD master flow:

```text
discuss -> plan -> execute -> verify
```

## Current Phase

| Field | Value |
|-------|-------|
| Phase | 2 |
| Name | Verified Logs Viewer |
| Status | Complete |
| Requirements | LOGS-01, LOGS-02, LOGS-03 |
| Current command | `/gsd-discuss-phase 2` run inline because `gsd-sdk` is unavailable |
| Next command | `/gsd-discuss-phase 3` when ready to plan verified service actions |

## Session Plan

Phase 1 was executed as a complete manual GSD loop:

```text
discuss -> plan -> execute -> verify
```

Atomic tasks:

1. Lock read-only MVP scope, planning state, and safety contract.
2. Implement the FastAPI read-only backend and status dashboard.
3. Verify endpoints, local binding, secrets safety, and absence of write actions.

## Latest Verification

**Verified:** 2026-06-03

- Python syntax compilation passed for `backend` and `tests`.
- Pytest passed: 4 tests.
- Local server started on `127.0.0.1:8787`.
- Curl checks passed for `/api/status`, `/api/system`, and `/api/hermes/status`.
- Hermes status returned safe `not_detected` state when Hermes was not found locally.
- Security search found no write-action routes, `shell=True`, unsafe flag, or credentials indicators outside Notion exports.
- `.env` is not tracked by git.
- `ALLOW_UNSAFE_COMMANDS=false` remains in `.env.example`.

## Phase 2 Log Source Findings

**Verified on Bob via read-only metadata inspection:** 2026-06-03

- Bob hostname: `Truls-sin-Mac-mini.local`
- Bob user: `trulsdahl`
- LaunchAgent plist: `/Users/trulsdahl/Library/LaunchAgents/ai.hermes.gateway.plist`
- LaunchAgent label: `ai.hermes.gateway`
- Working directory: `/Users/trulsdahl/.hermes/hermes-agent`
- Program arguments: `/Users/trulsdahl/.hermes/hermes-agent/venv/bin/python -m hermes_cli.main gateway run --replace`
- StandardOutPath: `/Users/trulsdahl/.hermes/logs/gateway.log`
- StandardErrorPath: `/Users/trulsdahl/.hermes/logs/gateway.error.log`

**Candidate sources, not enabled by default yet:**

- `/Users/trulsdahl/.hermes/logs/agent.log`
- `/Users/trulsdahl/.hermes/logs/errors.log`
- Hermes UI backend log: TBD

## Open Gates

- Verify actual Hermes launchctl commands before implementing start, stop, or restart.
- Log display is implemented only from verified server-side allowlisted files.
- Keep Phase 1 read-only complete; future phases must not reintroduce write actions without their own verification.
- Keep real `.env` out of git.
- Keep `ALLOW_UNSAFE_COMMANDS=false`.
- Do not add Cloudflare configuration or credentials in this phase.
- Do not add any API route that accepts a file path from client input.

## Memory

- `docs/notion/` is authoritative source context.
- `127.0.0.1:8787` is the local binding target.
- Cloudflare Access is required for later external access.
- Free terminal in browser is out of scope.
- Phase 1 includes the first read-only MVP foundation, not write actions.
- Phase 2 implemented bounded read-only logs API for `gateway_stdout` and `gateway_stderr`.

## Phase 2 Verification

**Verified:** 2026-06-03

- `python3 -m compileall backend tests` passed.
- `.venv/bin/python -m pytest` passed: 10 tests.
- Curl checks passed for `/api/logs/sources`, `/api/logs/gateway_stdout`, and `/api/logs/gateway_stderr`.
- Missing local log files on dev machine returned safe structured errors without traceback.
- Security scan found no `shell=True`, no write-action routes, and no unsafe command/path API.

---
*Last updated: 2026-06-03 after Phase 2 implementation*
