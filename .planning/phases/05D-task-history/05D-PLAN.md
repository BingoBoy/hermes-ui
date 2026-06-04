# Phase 5D Plan: Bob Task History

**Status:** Executed locally 2026-06-04

## Delivered

- `GET /api/bob/tasks?limit=20` — kanban list, gated by `ALLOW_BOB_TASKS`
- `GET /api/bob/tasks/{task_id}` — kanban show, strict id validation, 404 on missing task
- Dashboard section «Bob-oppgaver» with refresh and detail panel

## Bob verification

```bash
curl -s http://127.0.0.1:8787/api/bob/tasks?limit=20 | python3 -m json.tool
curl -s http://127.0.0.1:8787/api/bob/tasks/t_79f256ed | python3 -m json.tool
```

Deploy: pull on Bob, restart `no.truls.hermes-ui` LaunchAgent.
