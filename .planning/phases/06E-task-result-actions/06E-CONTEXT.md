# Phase 6E — Task Result Actions — CONTEXT

**Created:** 2026-06-04  
**Status:** Locked for planning/execute

## Goal

Browser-only actions on Bob Inbox and task detail results: copy text/ID/title, expand long results — no backend writes.

## Decisions

- **D-01:** Frontend-only — no new routes; reuse `GET /api/bob/tasks` + `GET /api/bob/tasks/{id}` data already in cache/detail.
- **D-02:** Clipboard via `navigator.clipboard.writeText` with `document.execCommand('copy')` fallback.
- **D-03:** Copy feedback on button: «Kopiert» / «Kunne ikke kopiere» (~1.6s).
- **D-04:** Inbox cards: meta (ID + timestamps), expandable excerpt (>120 chars), «Kopier resultat», «Kopier ID», «Kopier tittel» (when present), keep «Vis detaljer».
- **D-05:** Detail panel: same copy toolbar on `#bob-detail-result-wrap`; «Vis mer» / «Vis mindre» on long `<pre>` result block.
- **D-06:** `ALLOW_BOB_TASKS` gate unchanged — inbox hidden when off.

## Files

| File | Change |
|------|--------|
| `backend/dashboard.py` | CSS + JS helpers + inbox/detail UI |
| `tests/test_api.py` | Assert copy/expand symbols and labels |
| `docs/api/bob-interaction.md`, `docs/security/README.md`, `README.md` | 6E subsection |

## Security

Copy/expand are client-only; no CLI, shell, or state mutation.
