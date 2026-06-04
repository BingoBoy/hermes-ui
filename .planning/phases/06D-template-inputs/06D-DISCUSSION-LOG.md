# Phase 6D — Template Inputs — DISCUSSION LOG

**Date:** 2026-06-04

## Current state (6C)

- `BOB_TASK_TEMPLATES` in `backend/dashboard.py` — five hardcoded `{ id, label, title, body }`.
- `submitBobTaskPayload({ title, body })` POSTs to `/api/bob/tasks` with shared result handling.
- `sendBobTaskTemplate(templateId)` finds template, POSTs fixed title/body.
- UI: `#bob-task-templates` with five `.bob-template-btn` one-click buttons above manual form.
- Gate: `updateBobTasksUi` hides templates + form when `ALLOW_BOB_TASKS=false`.
- Tests: `test_dashboard_includes_bob_task_templates_ui` in `tests/test_api.py`.

## Backend unchanged?

**Yes.** POST contract is `{ title, body }` only. Composing body from optional inputs is client-side.

## Minimal change

1. Add optional `inputLabel` / `maxlength` metadata to each template (or parallel map).
2. Add `buildBobTaskTemplatePayload(templateId, inputValue)` to merge inputs into `body`.
3. Replace button grid with per-template field + «Send mal til Bob».
4. Wire `sendBobTaskTemplate` to read input and call `buildBobTaskTemplatePayload` before `submitBobTaskPayload`.
5. Extend tests and docs.

## UI choice

Per-template row (input + send) — fits existing `.bob-form` / `.field` styles without a select-wizard step.

## Gray areas resolved without user prompt

User supplied full spec in request; no additional discuss areas required.
