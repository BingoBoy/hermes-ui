# Phase 6D — Template Inputs — VERIFICATION

**Date:** 2026-06-04

## Goal-backward

| Criterion | Status |
|-----------|--------|
| Optional inputs on relevant templates | PASS — five template rows with fields |
| Same POST /api/bob/tasks | PASS — `submitBobTaskPayload` unchanged |
| No new backend routes | PASS — `test_only_allowlisted_write_route_exists` |
| Manual form still works | PASS — `submitBobTask` + form unchanged |
| ALLOW_BOB_TASKS gate | PASS — `updateBobTasksUi` hides `#bob-task-templates` |
| Inputs → plain text in body only | PASS — `buildBobTaskTemplatePayload` client-side |
| No terminal/chat/shell/CLI flags | PASS — security greps clean |

## Tests

```
.venv/bin/python -m pytest -q → 63 passed
```

## Security checks

- `grep shell=True backend/` — no matches
- `grep hermes -z backend/` — no matches
- Write routes unchanged: POST `/api/bob/tasks`, POST `/api/hermes/restart` only

## npm

No `package.json` in repo — lint/build scripts N/A.

## Deploy

- Pushed to `origin/main` (5355872, d380068, d2abf42)
- Bob: pull + kickstart 2026-06-04; `/api/status` ok

## External UAT (user)

**URL:** https://hermes-ui.strategistudio.no (Cloudflare Access)

| # | Check | Result |
|---|-------|--------|
| 1 | Bob task-maler visible | PASS |
| 2 | Input fields on relevant templates | PASS |
| 3 | Morgenbrief without input | PASS |
| 4 | Morgenbrief with optional focus | PASS |
| 5 | Nettsideanalyse with URL | PASS |
| 6 | Konkurrentanalyse with tema | PASS |
| 7 | Tasks appear in Bob-oppgaver | PASS |
| 8 | Manual form works | PASS |
| 9 | Bob Inbox works | PASS |
| 10 | Gateway logs work | PASS |
| 11 | Restart Gateway works | PASS |
| 12 | No terminal/chat/gateway start/stop | PASS |

**Verdict:** Phase 6D verified (automated + Bob + user UAT).
