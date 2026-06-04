# State: Hermes UI for Bob

## Project Reference

See: `.planning/PROJECT.md` (updated 2026-06-03)

**Core value:** Truls can safely see whether Bob and Hermes are healthy without exposing shell access, secrets, or unsafe service controls.

**Current focus:** Phase 5 - Verified Service Actions

## Workflow

Use original GSD master flow:

```text
discuss -> plan -> execute -> verify
```

## Current Phase

| Field | Value |
|-------|-------|
| Phase | 4 |
| Name | Cloudflare Access and Tunnel |
| Status | Complete |
| Requirements | OPS-01, SEC-04 |
| Current command | `/gsd-execute-phase 4` completed as docs verification |
| Next command | `/gsd-discuss-phase 5` for verified service actions |

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

**Verified:** 2026-06-04

- Hermes UI exposed at `https://hermes-ui.strategistudio.no`
- Unauthenticated curl to `/api/status` returns HTTP `302` to Cloudflare Access login
- Backend on Bob remains bound to `127.0.0.1:8787`
- `.venv/bin/python -m pytest` passed: 10 tests
- No backend code changed in Phase 4 documentation commit
- No secrets committed to git

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

## Phase 4 Cloudflare Deployment

**Verified on:** 2026-06-04

- Public URL: `https://hermes-ui.strategistudio.no`
- Tunnel name: `bob-mac-mini-m4`
- Route type: Published application route
- Service target: `http://127.0.0.1:8787`
- Access application: Self-hosted application
- Access policy: `Only Truls` pattern
- Local `config.yml`: not created
- New tunnel created: no
- Tunnel model: token-based / Cloudflare-managed
- Unauthenticated curl: HTTP `302` redirect to Cloudflare Access login

## Open Gates

- Verify actual Hermes launchctl commands before implementing start, stop, or restart in UI.
- Log display is implemented only from verified server-side allowlisted files.
- Keep Phase 1 read-only complete; future phases must not reintroduce write actions without their own verification.
- Keep real `.env` out of git.
- Keep `ALLOW_UNSAFE_COMMANDS=false`.
- Do not add any API route that accepts a file path from client input.

## Memory

- `docs/notion/` is authoritative source context.
- `127.0.0.1:8787` is the local binding target.
- External access is live at `https://hermes-ui.strategistudio.no` behind Cloudflare Access.
- Free terminal in browser is out of scope.
- Phase 1 includes the first read-only MVP foundation, not write actions.
- Phase 2 implemented bounded read-only logs API for `gateway_stdout` and `gateway_stderr`.
- Phase 3 documented verified Hermes UI LaunchAgent deployment on Bob.
- Phase 4 deployed and documented Cloudflare Tunnel and Access exposure.

## Phase 4 Verification

**Verified:** 2026-06-04

- Docs-only change in repo: no backend or test code modified.
- External curl check returned HTTP `302` to Cloudflare Access login for unauthenticated `/api/status`.
- Secret scan found no committed `.env`, credentials, or token material added by this phase.
- `.venv/bin/python -m pytest` passed: 10 tests.

---
*Last updated: 2026-06-04 after Phase 4 Cloudflare deployment documentation*
