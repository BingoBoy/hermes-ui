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

Pending push + Bob pull (see session report).
