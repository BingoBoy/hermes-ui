# Phase 3: Document Bob LaunchAgent Deployment - Plan

**Created:** 2026-06-03
**Status:** Complete
**Scope:** Documentation and GSD state only — no runtime code changes

## Goal

Document that Hermes UI runs as a verified LaunchAgent on Bob, including operational commands, log paths, local binding, and the forward Cloudflare plan.

## Verified Bob Facts

| Field | Verified value |
|-------|----------------|
| Hostname | `Truls-sin-Mac-mini.local` |
| User | `trulsdahl` |
| LaunchAgent label | `no.truls.hermes-ui` |
| LaunchAgent plist | `/Users/trulsdahl/Library/LaunchAgents/no.truls.hermes-ui.plist` |
| Working directory | `/Users/trulsdahl/Dev/hermes-ui` |
| Program | `/Users/trulsdahl/Dev/hermes-ui/.venv/bin/uvicorn backend.main:app --host 127.0.0.1 --port 8787` |
| StandardOutPath | `/Users/trulsdahl/.hermes-ui/logs/hermes-ui.log` |
| StandardErrorPath | `/Users/trulsdahl/.hermes-ui/logs/hermes-ui.error.log` |
| Bind address | `127.0.0.1:8787` |
| API status | `ok` |
| `read_only` | `true` |
| `allow_unsafe_commands` | `false` |

## Atomic Tasks

### Task 1 - README Bob Operations

**Output:** Updated `README.md`

**Acceptance criteria:**
- Documents LaunchAgent start, stop, restart, and status checks.
- Documents Hermes UI log paths and how to tail them.
- Documents local API smoke tests on Bob.
- Keeps manual dev run instructions for non-Bob environments.

### Task 2 - Deployment Architecture Doc

**Output:** `docs/architecture/deployment.md`

**Acceptance criteria:**
- Documents local binding on `127.0.0.1:8787`.
- Documents launchd/LaunchAgent layout and verified plist fields.
- Documents Hermes UI log paths.
- Documents forward Cloudflare Tunnel and Access plan without implementing it.

### Task 3 - GSD State and Verification

**Output:** Updated `.planning/STATE.md` and `.planning/ROADMAP.md`

**Acceptance criteria:**
- Phase 3 marked complete with Bob LaunchAgent verification recorded.
- Next phase points to Cloudflare Access/Tunnel.
- Verification confirms docs-only change: no `.env`, no secrets, pytest still passes.

## Completion

Phase 3 completed on 2026-06-03:

- README updated with Bob LaunchAgent operations.
- `docs/architecture/deployment.md` created.
- GSD state and roadmap updated.
- Verification passed: docs-only, no secrets added, pytest green.

*Plan created: 2026-06-03*
*Plan completed: 2026-06-03*
