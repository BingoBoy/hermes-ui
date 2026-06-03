# Cloudflare Architecture: Hermes UI External Access

## Purpose

This document plans secure external access to Hermes UI on Bob through Cloudflare Tunnel and Cloudflare Access. It is planning documentation only. No Cloudflare configuration is applied by this repo phase.

## Target Architecture

```text
Browser / MacBook / phone
  -> Cloudflare Access (Zero Trust)
  -> Cloudflare Tunnel (cloudflared on Bob)
  -> http://127.0.0.1:8787
  -> Hermes UI FastAPI (read-only)
```

Rules:

- Hermes UI stays bound to `127.0.0.1:8787`.
- The tunnel forwards traffic to loopback only.
- No router port forwarding is used.
- No backend binding to `0.0.0.0`.

## Verified Preconditions on Bob

Inspected read-only on 2026-06-03.

| Field | Verified value |
|-------|----------------|
| Hostname | `Truls-sin-Mac-mini.local` |
| User | `trulsdahl` |
| Hermes UI bind | `127.0.0.1:8787` |
| Hermes UI LaunchAgent | `no.truls.hermes-ui` |
| `cloudflared` binary | `/opt/homebrew/bin/cloudflared` |
| `cloudflared` version | `2026.5.1` |
| DNS zone | `strategistudio.no` |
| Zero Trust domain pattern | `strategistudio.cloudflareaccess.com` |
| Existing Access-protected SSH | `bob-ssh.strategistudio.no` |
| `cloudflared tunnel list` | Requires origin cert via `cloudflared tunnel login` |

## Recommended Public Identity

| Item | Recommendation | Notes |
|------|----------------|-------|
| Primary hostname | `https://hermes.strategistudio.no` | Preferred public URL |
| Fallback hostname | `https://hermes-ui.strategistudio.no` | Use only if `hermes` is unavailable |
| Tunnel name | `mac-mini-m4-tunnel` | Dedicated Bob Mac Mini M4 tunnel |
| Ingress service | `http://127.0.0.1:8787` | Must not point to LAN IP or `0.0.0.0` |
| Access policy | `Only Truls` pattern | Match existing internal apps |

Do not route Hermes UI through the legacy shared tunnel `kokebok-web`. Keep Hermes UI on a Bob-specific tunnel plan.

## Cloudflare Access Requirements

Before the public URL is used:

1. Create a Zero Trust application for `hermes.strategistudio.no`.
2. Attach an Access policy that allows only authorized users.
3. Verify unauthenticated requests stop at Cloudflare Access.
4. Do not embed Access tokens in Hermes UI backend code for MVP.

Access protects the entire application surface, including:

- Dashboard `/`
- Read-only API routes under `/api/*`

## Tunnel and Ingress Plan

### 1. Authenticate and inspect tunnels

Run on Bob:

```bash
/opt/homebrew/bin/cloudflared --version
/opt/homebrew/bin/cloudflared tunnel login
/opt/homebrew/bin/cloudflared tunnel list
/opt/homebrew/bin/cloudflared tunnel info mac-mini-m4-tunnel
```

If the tunnel does not exist:

```bash
/opt/homebrew/bin/cloudflared tunnel create mac-mini-m4-tunnel
/opt/homebrew/bin/cloudflared tunnel info mac-mini-m4-tunnel
```

### 2. Route DNS

```bash
/opt/homebrew/bin/cloudflared tunnel route dns mac-mini-m4-tunnel hermes.strategistudio.no
```

### 3. Ingress configuration

Store config locally on Bob, not in git. Example shape:

```yaml
tunnel: mac-mini-m4-tunnel
credentials-file: /Users/trulsdahl/.cloudflared/<TUNNEL-UUID>.json

ingress:
  - hostname: hermes.strategistudio.no
    service: http://127.0.0.1:8787
  - service: http_status:404
```

Notes:

- Replace `<TUNNEL-UUID>` with the actual tunnel credential filename on Bob.
- Never commit the credentials JSON file.
- Keep a catch-all `http_status:404` rule last.

### 4. Run or install the tunnel

Manual test run:

```bash
/opt/homebrew/bin/cloudflared tunnel --config ~/.cloudflared/config.yml run mac-mini-m4-tunnel
```

After verification, install persistence through LaunchAgent or:

```bash
/opt/homebrew/bin/cloudflared service install
```

Choose one persistence model and document the final choice during execution.

## Verification Sequence

### Local verification on Bob

Run before any external test:

```bash
launchctl list | grep hermes-ui
lsof -nP -iTCP:8787 -sTCP:LISTEN
curl -s http://127.0.0.1:8787/api/status | python3 -m json.tool
curl -s http://127.0.0.1:8787/api/hermes/status | python3 -m json.tool
curl -s http://127.0.0.1:8787/api/logs/sources | python3 -m json.tool
```

Expected:

- Hermes UI LaunchAgent loaded
- Port `8787` listening on `127.0.0.1` only
- `"read_only": true`
- `"allow_unsafe_commands": false`

### External verification after Access

From a device outside the local network:

1. Open `https://hermes.strategistudio.no`
2. Confirm Cloudflare Access login appears
3. Sign in with authorized identity
4. Confirm dashboard loads
5. Confirm no write-action controls appear

Optional header check:

```bash
curl -I https://hermes.strategistudio.no/
curl -I https://hermes.strategistudio.no/api/status
```

Unauthenticated clients should not receive Hermes UI content directly.

## Secrets and Configuration Boundaries

Keep local only on Bob:

- `~/.cloudflared/<TUNNEL-UUID>.json`
- `~/.cloudflared/cert.pem` after `cloudflared tunnel login`
- `.env` with any future `HERMES_UI_PUBLIC_URL`
- Cloudflare Access org tokens or service tokens

Tracked in repo:

- `.env.example` placeholders only
- Documentation patterns and command examples without secret values

Never commit or paste into Notion:

- Tunnel credential JSON contents
- Access service tokens
- API tokens
- Private keys
- Real `.env` contents

## Post-Go-Live Local Setting

After external access is verified, set on Bob only:

```text
HERMES_UI_PUBLIC_URL=https://hermes.strategistudio.no
```

Do not add this to git. Update Bob LaunchAgent environment or local `.env` during execution.

## Explicit Non-Actions in Planning Phase

This planning phase did not:

- create or modify Cloudflare tunnels
- add DNS records
- create Access applications
- install a persistent `cloudflared` service
- change Hermes UI backend code
- bind Hermes UI to `0.0.0.0`

## Related Documents

- `docs/architecture/deployment.md` — Bob LaunchAgent and local binding
- `docs/security/README.md` — security gates and secret handling
- `.planning/phases/04-cloudflare-access-tunnel/04-PLAN.md` — execution checklist
