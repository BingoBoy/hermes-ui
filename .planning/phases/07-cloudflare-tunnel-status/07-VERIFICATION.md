# Phase 7: Verification

**Date:** 2026-06-04  
**Status:** passed locally — Bob deploy pending (SSH BobRemote unavailable at verify time)

## Local checks

```bash
.venv/bin/python -m pytest -q
grep -R "shell=True" backend/ || true
grep -R "hermes -z" backend/ || true
grep -R "tunnel list" backend/ || true
```

| Check | Result |
|-------|--------|
| pytest | **PASS** — 80 passed |
| shell=True | **PASS** — no matches |
| hermes -z | **PASS** — no matches |
| tunnel list in backend | **PASS** — no matches |
| POST routes | **PASS** — only `/api/hermes/restart`, `/api/bob/tasks` (test_api allowlist) |
| `cloudflare_tunnel` in operations | **PASS** — test_operations |
| Edge 302 mock | **PASS** — test_cloudflare_tunnel_edge_probe_302 |
| Path redaction | **PASS** — test_cloudflare_tunnel_redacts_cloudflared_paths |
| Dashboard HTML | **PASS** — Cloudflare Tunnel, operations-tunnel-wrap, disclaimer |

## Bob checks (pending — run manually)

BobRemote SSH failed with `websocket: bad handshake` during automated 7.5. After connectivity returns:

```bash
cd /Users/trulsdahl/Dev/hermes-ui
git pull --ff-only origin main
launchctl kickstart -k gui/$(id -u)/no.truls.hermes-ui
curl -s http://127.0.0.1:8787/api/operations | python3 -m json.tool
curl -s http://127.0.0.1:8787/ | grep -i "Cloudflare Tunnel" -A 20
```

Expected:

- `cloudflare_tunnel.public_hostname` = `hermes-ui.strategistudio.no`
- `cloudflare_tunnel.tunnel_name` = `bob-mac-mini-m4`
- `edge_probe.http_status` = 302 (or documented actual)
- `edge_probe.access_redirect` = true when 302 to cloudflareaccess.com
- No credential paths or tokens in JSON/HTML

## Requirements

| ID | Status | Notes |
|----|--------|-------|
| OPS-01 | partial | Code + tests; Bob UAT pending |
| OPS-02 | pass | Fixed argv via _run_read_only |
| OPS-03 | pass | No secrets in tests; redaction for pgrep |
| SEC-01 | pass | No new POST routes |
| SEC-02 | pass | No shell=True |

## Git

- `88d9964` — feat(07): add read-only Cloudflare tunnel status

## Next

- `/gsd-verify-work 7` after Bob manual curl confirms payload
- Or re-run Bob deploy when SSH stable, then `/gsd-ship 7`
