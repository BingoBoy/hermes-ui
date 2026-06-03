# State: Hermes UI for Bob

## Project Reference

See: `.planning/PROJECT.md` (updated 2026-06-03)

**Core value:** Truls can safely see whether Bob and Hermes are healthy without exposing shell access, secrets, or unsafe service controls.

**Current focus:** Phase 4 - Cloudflare Access and Tunnel

## Workflow

Use original GSD master flow:

```text
discuss -> plan -> execute -> verify
```

## Current Phase

| Field | Value |
|-------|-------|
| Phase | 3 |
| Name | Document Bob LaunchAgent Deployment |
| Status | Complete |
| Requirements | RUN-01, RUN-02, OPS-02 |
| Current command | `/gsd-plan-phase 3` executed as docs-only phase |
| Next command | `/gsd-discuss-phase 4` for Cloudflare Access and Tunnel |

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
- Pytest passed: 10 tests.
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
- Hermes UI backend log: verified on disk, not yet in logs API allowlist

## Phase 3 Bob LaunchAgent Findings

**Verified on Bob via read-only inspection:** 2026-06-03

- Hermes UI LaunchAgent label: `no.truls.hermes-ui`
- Hermes UI LaunchAgent plist: `/Users/trulsdahl/Library/LaunchAgents/no.truls.hermes-ui.plist`
- Working directory: `/Users/trulsdahl/Dev/hermes-ui`
- Program: `/Users/trulsdahl/Dev/hermes-ui/.venv/bin/uvicorn backend.main:app --host 127.0.0.1 --port 8787`
- StandardOutPath: `/Users/trulsdahl/.hermes-ui/logs/hermes-ui.log`
- StandardErrorPath: `/Users/trulsdahl/.hermes-ui/logs/hermes-ui.error.log`
- Bind address: `127.0.0.1:8787`
- API status: `ok`
- `read_only`: `true`
- `allow_unsafe_commands`: `false`

## Open Gates

- Verify actual Hermes launchctl commands before implementing start, stop, or restart in UI.
- Log display is implemented only from verified server-side allowlisted files.
- Keep Phase 1 read-only complete; future phases must not reintroduce write actions without their own verification.
- Keep real `.env` out of git.
- Keep `ALLOW_UNSAFE_COMMANDS=false`.
- Cloudflare Tunnel and Access are planned but not configured yet.
- Do not add any API route that accepts a file path from client input.

## Memory

- `docs/notion/` is authoritative source context.
- `127.0.0.1:8787` is the local binding target.
- Cloudflare Access is required for later external access.
- Free terminal in browser is out of scope.
- Phase 1 includes the first read-only MVP foundation, not write actions.
- Phase 2 implemented bounded read-only logs API for `gateway_stdout` and `gateway_stderr`.
- Phase 3 documented verified Hermes UI LaunchAgent deployment on Bob.

## Phase 2 Verification

**Verified:** 2026-06-03

- `python3 -m compileall backend tests` passed.
- `.venv/bin/python -m pytest` passed: 10 tests.
- Curl checks passed for `/api/logs/sources`, `/api/logs/gateway_stdout`, and `/api/logs/gateway_stderr`.
- Missing local log files on dev machine returned safe structured errors without traceback.
- Security scan found no `shell=True`, no write-action routes, and no unsafe command/path API.

## Phase 3 Verification

**Verified:** 2026-06-03

- Docs-only change: no backend or test code modified.
- Bob LaunchAgent metadata verified via read-only SSH inspection.
- `git status` confirmed documentation and planning updates only.
- Secret scan found no committed `.env` or credential material.
- `.venv/bin/python -m pytest` passed: 10 tests.

---
*Last updated: 2026-06-03 after Phase 3 documentation*
