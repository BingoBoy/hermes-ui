# Phase 7 Discussion Log

**Date:** 2026-06-04  
**Mode:** Directed discuss (user-supplied gray areas, no implementation)

## Questions resolved

### 1. Safest tunnel status read on Bob?

**Answer:** Fixed-argv local inspection only: `cloudflared --version`, `pgrep`/`ps` for process, optional `curl -D` to public hostname for HTTP status (302 = Access gate). **Not** `cloudflared tunnel list`, **not** credential files, **not** Cloudflare API tokens.

### 2. launchctl vs process vs plist vs logs vs API?

| Method | Verdict |
|--------|---------|
| Process check (`pgrep`) | **Primary** |
| `cloudflared --version` | **Primary** |
| External curl (status code only) | **Secondary** — edge health |
| launchctl | **Conditional** — only if Bob has stable cloudflared LaunchAgent label |
| Plist under `.cloudflared` | **Reject** — secrets |
| Log tail of cloudflared | **Reject** — not needed for OPS-01; log noise |
| Cloudflare API | **Reject** — tokens |

### 3. Safe UI fields?

Hostname, tunnel name, service target, binary installed/version, process running, edge HTTP status / Access redirect indicator, checked_at. No credentials, no config JSON, no response bodies.

### 4. `/api/operations` vs new route?

**Extend `GET /api/operations`** with `cloudflare_tunnel` object. Same dashboard section. No new route unless plan discovers strong reason (unlikely).

### 5. Tests?

Extend `test_operations.py`, mock subprocess, keep `test_api.py` route guards, Bob curl after deploy.

### 6. Security boundaries?

No shell, no new POST, allowlisted argv, timeouts, fail closed, settings-driven hostname only.

### 7. Minimal plan sketch for `/gsd-plan-phase 7`

1. **7.0 Bob preflight** — document results in plan (which probes work).
2. **7.1 Settings** — hostname, tunnel name, edge probe flag in config + `.env.example`.
3. **7.2 Backend** — `_cloudflare_tunnel_status()` in `operations.py`, wire into `get_operations_status`.
4. **7.3 Dashboard** — extend `renderOperations` with Tunnel block.
5. **7.4 Tests** — operations payload + mocks.
6. **7.5 Verify** — pytest, Bob `/api/operations`, optional external browser check (Access login still expected).

## User constraints acknowledged

- Read-only only; no write-actions; no secrets; no tunnel control; no 5B; no LM Studio/n8n; no worker assignee changes.
- Build on Phase 6, not greenfield ops module.
