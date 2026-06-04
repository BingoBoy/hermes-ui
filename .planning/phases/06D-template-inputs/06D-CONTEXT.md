# Phase 6D — Template Inputs — CONTEXT

**Created:** 2026-06-04  
**Status:** Locked for planning/execute

## Goal

Add safe optional input fields to Bob task templates. Inputs compose plain-text task `body` in the browser before the existing `submitBobTaskPayload` → `POST /api/bob/tasks` flow.

## Decisions

- **D-01:** Frontend-only — no new backend routes, no Python changes unless POST contract breaks (it does not).
- **D-02:** Reuse `submitBobTaskPayload`, `sendBobTaskTemplate`, and `ALLOW_BOB_TASKS` gate via `updateBobTasksUi` (templates section hidden when gate off).
- **D-03:** Replace one-click-only buttons with compact per-template rows: optional input + «Send mal til Bob» (keeps section light, no modal wizard).
- **D-04:** Input values are trimmed plain text only — appended or woven into hardcoded `body` strings in JS; never passed as CLI flags or route parameters.
- **D-05:** Per-template labels (Norwegian): Morgenbrief «Fokus for dagen»; Ukesrapport «Periode»; Konkurrentanalyse «Konkurrent eller tema»; Nettsideanalyse «URL som skal analyseres»; Markedsføring «Fokusområde».
- **D-06:** Composition rules match user spec (morgenbrief append «Dagens fokus»; ukesrapport default «denne uken»; nettsideanalyse keep ask-for-URL instruction when empty).
- **D-07:** `setBobTaskCreateControlsDisabled` disables template inputs and send buttons during in-flight POST (same as 6C buttons + manual submit).
- **D-08:** Extend `test_dashboard_includes_bob_task_templates_ui` for input labels and `buildBobTaskTemplatePayload` (or equivalent) symbol in served HTML.

## Files (expected)

| File | Change |
|------|--------|
| `backend/dashboard.py` | Templates HTML/CSS/JS |
| `tests/test_api.py` | Assert input labels + compose helper |
| `docs/api/bob-interaction.md` | 6D subsection |
| `docs/security/README.md` | Template inputs boundary |
| `README.md` | Mention optional template fields |

## Security (unchanged)

- No terminal/chat/shell/`hermes -z`
- No client CLI flags
- No new write routes
- Inputs → task text only
