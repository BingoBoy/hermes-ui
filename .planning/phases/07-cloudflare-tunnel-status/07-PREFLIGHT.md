# Phase 7 Bob Preflight — Cloudflare Tunnel Observation

**Date:** 2026-06-04  
**Host:** Bob (Truls-sin-Mac-mini)  
**Note:** Execute-time SSH to BobRemote failed (`websocket: bad handshake`) during MacBook implement. Values below combine **prior Bob sessions** (Phase 4, Phase 6) and **code defaults**. Re-run checklist at deploy (7.5).

## Commands

```bash
which cloudflared
cloudflared --version
pgrep -lf cloudflared || true
launchctl list 2>/dev/null | grep -i cloudflared || true
curl -sS -D - -o /dev/null --max-time 5 --max-redirs 0 https://hermes-ui.strategistudio.no/api/status | head -20
cloudflared tunnel list 2>&1 | head -5   # confirm NOT used in code
```

## Recorded / expected results

| Check | Result | Notes |
|-------|--------|-------|
| `which cloudflared` | `/opt/homebrew/bin/cloudflared` | Phase 4 D-03 |
| `cloudflared --version` | `2026.5.1` (or current) | Phase 4 |
| `pgrep -lf cloudflared` | Process expected when tunnel connector runs | Primary running signal |
| `launchctl list \| grep cloudflared` | **No stable label found** | Token-managed tunnel; no dedicated label in Phase 4 docs |
| Edge probe | **HTTP 302** → `*.cloudflareaccess.com` | Phase 4 D-31; deployment.md |
| `cloudflared tunnel list` | Fails without `cert.pem` | **Do not implement** — confirmed Phase 4 D-06 |

## launchctl decision

**`HERMES_CLOUDFLARED_LAUNCHD_LABEL` left empty** — no repeatable cloudflared LaunchAgent label documented on Bob. `cloudflare_tunnel.launchctl.included = false` in API.

## Implementation defaults locked from preflight

- `HERMES_PUBLIC_HOSTNAME=hermes-ui.strategistudio.no`
- `HERMES_CLOUDFLARE_TUNNEL_NAME=bob-mac-mini-m4`
- `HERMES_OPS_EDGE_PROBE=true`
- `HERMES_CLOUDFLARED_BIN=/opt/homebrew/bin/cloudflared`

## Re-verify at 7.5

After deploy, run on Bob:

```bash
curl -s http://127.0.0.1:8787/api/operations | python3 -m json.tool
```

Confirm `cloudflare_tunnel` keys and no credential leakage.
