# Phase 6A–6B Plan

**Status:** Complete — dashboard-only, no backend route changes

## 6A — Task follow-up

- Status badges: ready, running, completed, failed, unknown
- Table columns: created/started/completed, result flag
- Auto-refresh toggle (12s)
- Result block in detail panel
- Highlight new task after submit

## 6B — Bob Inbox

- Section «Bob Inbox» with curated cards from cached list
- Max 8 items, excerpt of result, link to detail

## Verification

```bash
.venv/bin/python -m pytest
curl -s http://127.0.0.1:8787/api/bob/tasks?limit=20
```
