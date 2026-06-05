# Phase 7: Cloudflare Tunnel Status — Research

**Date:** 2026-06-04  
**Status:** Complete (planning-only; extends Phase 6 research)

## Constraint recap (from 07-CONTEXT.md)

- Extend `GET /api/operations` — no new route.
- Local observation only; no `cloudflared tunnel list`, no credential reads, no Cloudflare API tokens.
- UI must say **local agent observed** — not “full Cloudflare edge health”.

## Existing code to extend

| File | Role |
|------|------|
| `backend/status.py` | `_run_read_only` — reuse in `operations.py` |
| `backend/operations.py` | `get_operations_status()` — add `cloudflare_tunnel` key |
| `backend/config.py` | New settings fields |
| `backend/dashboard.py` | `#operations-tunnel-wrap`, extend `renderOperations()` |
| `tests/test_operations.py` | Payload shape + mocks |

## Bob observation commands (7.0 preflight)

```bash
which cloudflared
cloudflared --version
pgrep -lf cloudflared || true
launchctl list 2>/dev/null | grep -i cloudflared || true
curl -sS -D - -o /dev/null --max-time 5 https://hermes-ui.strategistudio.no/api/status 2>&1 | head -20
```

**Expected (Phase 4):**

- `cloudflared` at `/opt/homebrew/bin/cloudflared`
- Edge probe: HTTP **302** redirect toward Cloudflare Access
- `tunnel list` may fail without `cert.pem` — **do not use in implementation**

## Proposed JSON shape

```json
{
  "observation_scope": "local_agent_and_edge_probe",
  "disclaimer": "Local cloudflared and HTTP probe only; not full Cloudflare control-plane health.",
  "public_hostname": "hermes-ui.strategistudio.no",
  "tunnel_name": "bob-mac-mini-m4",
  "service_target": "http://127.0.0.1:8787",
  "cloudflared": {
    "installed": true,
    "binary_path": "/opt/homebrew/bin/cloudflared",
    "version": "cloudflared version 2026.5.1 (...)",
    "process_running": true,
    "process_summary": "truncated pgrep line"
  },
  "edge_probe": {
    "enabled": true,
    "attempted": true,
    "http_status": 302,
    "access_redirect": true,
    "location_host": "*.cloudflareaccess.com",
    "error": null
  },
  "launchctl": {
    "included": false,
    "reason": "no stable label in Bob preflight"
  }
}
```

## Edge probe implementation notes

- Build URL: `https://{settings.hermes_public_hostname}/api/status` (fixed path, no client input).
- argv: `curl`, `-sS`, `-D`, `-`, `-o`, `/dev/null`, `--max-time`, `5`, `--max-redirs`, `0`, url`.
- Parse first line for status code; parse `location:` header host only (no full URL with tokens).
- Set `access_redirect: true` when status is 302 and location host contains `cloudflareaccess.com` (case-insensitive).
- Never attach response body to JSON.

## Security

- Import `_run_read_only` from `backend.status` (no `shell=True`).
- Truncate `process_summary` to ~120 chars; strip lines containing `.cloudflared/` if present.
- `HERMES_OPS_EDGE_PROBE=false` skips external curl (tests/dev).

## Dashboard copy (Norwegian)

- Section title: **Cloudflare Tunnel**
- Intro: «Lokal observasjon av cloudflared og en enkel HTTP-probe mot offentlig URL. Viser ikke full Cloudflare edge-status.»
- Fields: Offentlig URL, Tunnel-navn, cloudflared, Prosess, Edge-probe (HTTP-kode), Access-viderekobling

## Not doing

- 5B, LM Studio, n8n, hermes-assignee, tunnel controls, Cloudflare API, `tunnel list`.
