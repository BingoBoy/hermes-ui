# Phase 7: Verification

**Date:** 2026-06-05  
**Status:** passed — local tests + Bob UAT after token redaction fix

## Local checks

```bash
.venv/bin/python -m pytest -q
grep -R "shell=True" backend/ || true
grep -R "hermes -z" backend/ || true
grep -R "cloudflared tunnel list" backend/ tests/ || true
```

| Check | Result |
|-------|--------|
| pytest | **PASS** — 81 passed |
| shell=True | **PASS** — no matches |
| hermes -z | **PASS** — no matches |
| tunnel list in backend/tests | **PASS** — no matches |
| POST routes | **PASS** — only `/api/hermes/restart`, `/api/bob/tasks` (test_api allowlist) |
| `cloudflare_tunnel` in operations | **PASS** — test_operations |
| Edge 302 mock | **PASS** — test_cloudflare_tunnel_edge_probe_302 |
| Path redaction | **PASS** — test_cloudflare_tunnel_redacts_cloudflared_paths |
| Token redaction | **PASS** — test_cloudflare_tunnel_redacts_tunnel_token |
| Dashboard HTML | **PASS** — Cloudflare Tunnel, operations-tunnel-wrap, disclaimer |

## Bob UAT — initial (before redaction fix)

**Commit:** `38b5b89`  
**Date:** 2026-06-05

Bob confirmed `/api/operations` structure and edge probe:

- `cloudflare_tunnel.observation_scope` = `local_agent_and_edge_probe`
- `public_hostname` = `hermes-ui.strategistudio.no`
- `tunnel_name` = `bob-mac-mini-m4`
- `service_target` = `http://127.0.0.1:8787`
- `cloudflared.installed` = true, `process_running` = true
- `edge_probe.http_status` = 302, `access_redirect` = true
- `location_host` = `strategistudio.cloudflareaccess.com`

**Finding:** `cloudflared.process_summary` leaked `--token eyJhIjoi...` from `pgrep -lf` argv. Violates OPS-03.

## Bob UAT — after redaction fix

**Commit:** `536cb94` — fix(07): redact cloudflared token from process summary  
**Deploy:** `git pull --ff-only origin main` + `launchctl kickstart` on BobRemote

```bash
curl -s http://127.0.0.1:8787/api/operations | python3 -m json.tool
curl -s http://127.0.0.1:8787/ | grep -i "Cloudflare Tunnel" -A 40
```

| Check | Result |
|-------|--------|
| `process_summary` | **PASS** — `tunnel run --token [redacted]` (no `eyJ`, no token value) |
| `edge_probe.http_status` | **PASS** — 302 |
| `edge_probe.access_redirect` | **PASS** — true |
| No `cert.pem` in JSON/HTML | **PASS** |
| No credentials JSON paths | **PASS** |
| Dashboard Cloudflare block | **PASS** — template present in HTML |

## Requirements

| ID | Status | Notes |
|----|--------|-------|
| OPS-01 | pass | Bob UAT confirms tunnel visibility |
| OPS-02 | pass | Fixed argv via _run_read_only |
| OPS-03 | pass | Token and `.cloudflared/` paths redacted in process_summary |
| SEC-01 | pass | No new POST routes |
| SEC-02 | pass | No shell=True |

## Git

- `88d9964` — feat(07): add read-only Cloudflare tunnel status
- `38b5b89` — docs(07): record Cloudflare tunnel status verification
- `536cb94` — fix(07): redact cloudflared token from process summary

## Next

- `/gsd-verify-work 7`
- `/gsd-ship 7`
