# State: Hermes UI for Bob

## Project Reference

See: `.planning/PROJECT.md` (updated 2026-06-03)

**Core value:** Truls can safely see whether Bob and Hermes are healthy without exposing shell access, secrets, or unsafe service controls.

**Current focus:** Phase 5A complete — restart-only service action; Phase 5B next

## Workflow

Use original GSD master flow:

```text
discuss -> plan -> execute -> verify
```

## Current Phase

| Field | Value |
|-------|-------|
| Phase | 5A |
| Name | Restart-only Verified Service Action |
| Status | Execute complete — pending Bob deploy verification |
| Requirements | ACT-03 (restart), ACT-04 (audit + confirmation) |
| Current command | `/gsd-execute-phase 5A` completed |
| Next command | Deploy to Bob, set `ALLOW_SERVICE_ACTIONS=true`, verify restart; then 5B |

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
- Dashboard UX improved with status badges, scrollable logs, and manual refresh
- `.venv/bin/python -m pytest` passed: 11 tests
- No write routes added
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

## Phase 4.5 Dashboard UX

**Completed on:** 2026-06-04

- Status cards use readable labels: Online/Offline, Running/Not running, Available/Unavailable
- Gateway logs render as scrollable readable lists
- Technical JSON preserved in collapsible sections
- Manual refresh button added
- Read-only API routes unchanged

## Phase 5 Planning Findings (2026-06-04)

**Track A — Service Actions (verified on Bob via SSH):**

| Action | Command | Status |
|--------|---------|--------|
| Status detail | `launchctl print gui/$(id -u)/ai.hermes.gateway` | Verified |
| Restart | `launchctl kickstart -k gui/$(id -u)/ai.hermes.gateway` | **Live verified** (PID changed) |
| Start | `launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/ai.hermes.gateway.plist` | Documented, not live-tested |
| Stop | `launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/ai.hermes.gateway.plist` | Documented, not live-tested |

Decision: use direct fixed `launchctl` argv (no `hermes gateway` CLI, no shell). First execute slice: **5A restart-only**.

**Track B — Bob Interaction (mapped on Bob):**

- No Hermes Gateway HTTP listen port for UI ingress.
- Primary recommended entry: `hermes kanban create` (5C).
- Read-only history: `hermes kanban list/show`, `hermes sessions list` (5D).
- Not recommended: `hermes -z`, browser chat, `hermes send`, arbitrary CLI flags from client.

Planning artifacts: `.planning/phases/05-verified-service-actions/`, `docs/api/service-actions.md`, `docs/api/bob-interaction.md`.

## Phase 5A Execute (2026-06-04)

**Implemented:**

- `backend/service_actions.py` — allowlisted restart, audit JSONL, 30s cooldown
- `POST /api/hermes/restart` — gated by `ALLOW_SERVICE_ACTIONS`
- Dashboard restart button + confirmation modal
- 25 pytest tests passing locally

**Not implemented:** start, stop, Bob task entry, chat, terminal

**Bob deploy gate:** set `ALLOW_SERVICE_ACTIONS=true` in local `.env`, restart Hermes UI LaunchAgent, test restart via dashboard.

## Phase 5C Discuss (2026-06-04)

**Scope:** Plan Bob task entry via `hermes kanban create` — no runtime code in discuss.

**Locked:**

- `POST /api/bob/tasks` with `{title, body}`; gate `ALLOW_BOB_TASKS=false`
- Fixed argv `create_kanban_task`; server idempotency key; 60s cooldown
- Audit `bob-interactions.log` (title hash, not full body)
- CLI contract verified **locally**; Bob re-verify required before execute

**Artifacts:** `.planning/phases/05C-bob-task-entry/`, updated `docs/api/bob-interaction.md`

**Next:** Truls runs Bob kanban verify commands → `/gsd-execute-phase 5C` or manual 3-task plan

## Open Gates

- Live-verify bootstrap/bootout before implementing start/stop (5B).
- Live-verify `hermes kanban create` JSON contract **on Bob** before enabling `ALLOW_BOB_TASKS` (5C execute).
- Set `ALLOW_SERVICE_ACTIONS=true` on Bob only when ready to test 5A execute.
- Log display remains server-side allowlisted only.
- Keep real `.env` out of git.
- Keep `ALLOW_UNSAFE_COMMANDS=false`.
- Do not add any API route that accepts a file path or shell command from client input.

## Memory

- `docs/notion/` is authoritative source context.
- `127.0.0.1:8787` is the local binding target.
- External access is live at `https://hermes-ui.strategistudio.no` behind Cloudflare Access.
- Free terminal in browser is out of scope.
- Phase 1 includes the first read-only MVP foundation, not write actions.
- Phase 2 implemented bounded read-only logs API for `gateway_stdout` and `gateway_stderr`.
- Phase 3 documented verified Hermes UI LaunchAgent deployment on Bob.
- Phase 4 deployed and documented Cloudflare Tunnel and Access exposure.
- Phase 4.5 improved read-only dashboard UX for daily operations.
- Phase 5 discuss mapped service actions and Bob entry; restart kickstart live-verified; 5A execute implemented locally.
- Phase 5C discuss locked kanban create API/UI/security; local CLI JSON verified; Bob verify pending before execute.

## Phase 4.5 Verification

**Verified:** 2026-06-04

- Dashboard test confirms status badges, refresh button, and log panels in HTML response.
- Existing API and logs tests still pass.
- Unauthenticated external curl still returns HTTP `302` to Cloudflare Access login.
- No write-action routes added.

## Phase 4 Verification

**Verified:** 2026-06-04

- Docs-only change in repo: no backend or test code modified.
- External curl check returned HTTP `302` to Cloudflare Access login for unauthenticated `/api/status`.
- Secret scan found no committed `.env`, credentials, or token material added by this phase.
- `.venv/bin/python -m pytest` passed: 11 tests.

---
*Last updated: 2026-06-04 after Phase 5A restart-only execute*
