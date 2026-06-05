# State: Hermes UI for Bob

## Project Reference

See: `.planning/PROJECT.md` (updated 2026-06-04)

**Core value:** Truls can safely see whether Bob and Hermes are healthy without exposing shell access, secrets, or unsafe service controls.

**Current focus:** Milestone **v1.1 Operational Visibility** — requirements + roadmap defined. **Phase 7** next (read-only Cloudflare tunnel status). No code started.

**Last activity:** 2026-06-04 — `/gsd-plan-phase 7`.

## Workflow

Use original GSD master flow:

```text
discuss -> plan -> execute -> verify
```

## Current Phase

| Field | Value |
|-------|-------|
| Phase | 7 |
| Name | Cloudflare Tunnel Status |
| Status | Planned — ready for execute |
| Requirements | OPS-01–03 (Phase 7) |
| Next command | `/gsd-execute-phase 7` |

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

**Next:** Truls runs Bob kanban verify commands → execute `05C-PLAN.md` (3 tasks)

## Phase 5C Execute (2026-06-04)

**Implemented:**

- `backend/bob_tasks.py` — kanban create, validation, 60s cooldown, audit JSONL
- `POST /api/bob/tasks` — gated by `ALLOW_BOB_TASKS`
- Dashboard «Send oppgave til Bob»
- 46 pytest tests passing locally

**Bob deploy gate:** set `ALLOW_BOB_TASKS=true` in plist/env after kanban verify on Bob; restart `no.truls.hermes-ui`.

## Phase 6A–6B Execute (2026-06-04)

**Implemented (dashboard only):**

- Bob-oppgaver follow-up: badges, auto-refresh 12s, result view, highlight new task
- Bob Inbox: up to 8 curated items from existing GET list API
- 62 pytest tests passing; no new write routes

## Phase 5D Execute (2026-06-04)

**Implemented:**

- `GET /api/bob/tasks` — `hermes kanban list --json`, limit 20 default / 50 max
- `GET /api/bob/tasks/{task_id}` — `hermes kanban show --json`, 404 on "no such task" even if exit 0
- Dashboard «Bob-oppgaver» med liste og detaljvisning
- 61 pytest tests passing locally

## Phase 5C Preflight (2026-06-04)

**Testmiljø:** OK — `pytest.ini` med `pythonpath = .`

## Open Gates

**Resolved on Bob (2026-06-04):**

- ~~Live-verify kanban create before `ALLOW_BOB_TASKS`~~ — Bob tasks live
- ~~Set `ALLOW_SERVICE_ACTIONS=true` for restart testing~~ — restart live on Bob

**Still open:**

- **5B:** Live-verify `launchctl bootstrap`/`bootout` for gateway start/stop in a maintenance window before any UI implementation.
- **Bob ops (external):** `hermes-assignee` missing in kanban-worker environment — blocks full worker completion, not Hermes UI API.
- **5B / ACT-01–02:** Deferred to v2 — not in v1.1; requires maintenance-window live verify.
- **OPS-EXT-01:** `hermes-assignee` — external Bob ops, not Hermes UI Phase 7–8.

**Standing security gates (unchanged):**

- Log display remains server-side allowlisted only (gateway logs today; Hermes UI logs not in allowlist).
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
- Phase 5 complete on Bob: restart (`ALLOW_SERVICE_ACTIONS`), Bob tasks (`ALLOW_BOB_TASKS`, assignee `default`), list/show APIs; 5B start/stop still blocked.
- Phase 6M shipped read-only Bob-oppgaver assignee labels (`Legacy unassigned` for ready tasks without assignee); no queue mutation.
- Delmilestone **2.1-bob-ux** archived 2026-06-04 — see `.planning/MILESTONES.md` and `.planning/milestones/v2.1-bob-ux-*`.
- Phase **6 Operations Enrichment** shipped 2026-06-04 — `GET /api/operations`, dashboard drift section.

## Phase 6 Ship (2026-06-04)

**Shipped:** direct to `main` (no feature-branch PR).

**Commits:** `8632f49` feat(6), `47d8276` docs(6) verify.

**Production:** Bob `/api/operations` read_only; both LaunchAgents running; docker disabled_by_config.
- Bob UX informal requirements archived; main `REQUIREMENTS.md` v1 traceability unchanged.

## Deferred Items (acknowledged at v2.1-bob-ux close)

| Category | Item | Status |
|----------|------|--------|
| ops | `hermes-assignee` missing in Bob kanban-worker environment | external |
| planning | v1 REQUIREMENTS.md checkboxes not migrated to PROJECT Validated | deferred to project milestone |
| verification | 06A–06B no dedicated VERIFICATION.md | accepted |

## Phase 6M Ship (2026-06-04)

**Shipped:** direct to `main` (no feature-branch PR).

**Commits:**

- `1cd4e06` — feat(6M): label bob task assignees (`backend/dashboard.py`, `tests/test_api.py`)
- `16d1da6` — docs(6M): record bob queue hygiene verification

**Verification:** `.planning/phases/06M-bob-task-queue-hygiene/06M-VERIFICATION.md` — all PASS; Bob at `1cd4e06`.

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
*Last updated: 2026-06-04 — v1.1 milestone started*
