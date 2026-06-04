# Cloudflare Architecture: Hermes UI External Access

## Purpose

This document describes how Hermes UI on Bob is exposed externally through Cloudflare Tunnel and Cloudflare Access.

## Live Architecture

```text
Browser / MacBook / phone
  -> Cloudflare Access (Zero Trust)
  -> Cloudflare Tunnel (bob-mac-mini-m4, managed in Cloudflare)
  -> http://127.0.0.1:8787
  -> Hermes UI FastAPI (read-only)
```

Rules in production:

- Hermes UI stays bound to `127.0.0.1:8787` on Bob.
- The tunnel route targets loopback only.
- No router port forwarding is used.
- No backend binding to `0.0.0.0`.

## Verified Deployment

Verified on 2026-06-04.

| Field | Actual value |
|-------|--------------|
| Public URL | `https://hermes-ui.strategistudio.no` |
| Tunnel name | `bob-mac-mini-m4` |
| Route type | Published application route |
| Route management | Cloudflare Dashboard |
| Service target | `http://127.0.0.1:8787` |
| Local bind on Bob | `127.0.0.1:8787` |
| Hermes UI LaunchAgent | `no.truls.hermes-ui` |
| Access application type | Self-hosted application |
| Access policy | `Only Truls` pattern |
| Local `config.yml` | Not created |
| New tunnel created | No — existing `bob-mac-mini-m4` reused |
| Tunnel credential model | Token-based / Cloudflare-managed |

## Planning vs Actual

| Item | Phase 4 plan | Actual deployment |
|------|--------------|-------------------|
| Hostname | `hermes.strategistudio.no` | `hermes-ui.strategistudio.no` |
| Tunnel name | `mac-mini-m4-tunnel` | `bob-mac-mini-m4` |
| Route setup | Local `config.yml` + CLI | Published application route in Cloudflare Dashboard |
| New tunnel | Create dedicated tunnel | Reused existing active tunnel |

## Cloudflare Access

Cloudflare Access is active for the public hostname.

Behavior:

- Unauthenticated requests are blocked at Cloudflare Access.
- Authenticated users reach Hermes UI through the tunnel.
- Access protects dashboard `/` and read-only API routes under `/api/*`.
- Hermes UI backend does not implement its own external auth layer for MVP.

Verified unauthenticated behavior:

```bash
curl -sS -D - -o /dev/null https://hermes-ui.strategistudio.no/api/status
```

Expected:

- HTTP `302`
- Redirect to `https://strategistudio.cloudflareaccess.com/cdn-cgi/access/login/...`
- No Hermes UI JSON body without Access login

## Tunnel Route

The route was added in Cloudflare Dashboard under **Published application routes** for tunnel `bob-mac-mini-m4`:

| Field | Value |
|-------|-------|
| Hostname | `hermes-ui.strategistudio.no` |
| Service | `http://127.0.0.1:8787` |
| Route type | Published application route |

Notes:

- No Bob-local ingress `config.yml` was created for this route.
- The tunnel remains token-based and managed through Cloudflare.
- Do not route Hermes UI through unrelated legacy tunnels such as `kokebok-web`.

## Local Verification on Bob

Run on Bob to confirm the backend remains healthy locally:

```bash
launchctl list | grep hermes-ui
lsof -nP -iTCP:8787 -sTCP:LISTEN
curl -s http://127.0.0.1:8787/api/status | python3 -m json.tool
```

Expected:

- Hermes UI LaunchAgent loaded
- Port `8787` listening on `127.0.0.1` only
- `"read_only": true`
- `"allow_unsafe_commands": false`

## External Verification

From an external client without Access credentials:

```bash
curl -sS -D - -o /dev/null https://hermes-ui.strategistudio.no/api/status
```

Expected: Cloudflare Access redirect (`302`), not direct API JSON.

From an authenticated browser session:

1. Open `https://hermes-ui.strategistudio.no`
2. Complete Cloudflare Access login
3. Confirm dashboard loads
4. Confirm read-only behavior remains unchanged

## Useful Inspection Commands

These commands are for operational inspection only. They must not be pasted into git with secret output.

```bash
/opt/homebrew/bin/cloudflared --version
/opt/homebrew/bin/cloudflared tunnel list
/opt/homebrew/bin/cloudflared tunnel info bob-mac-mini-m4
```

Do not commit tunnel tokens, credential JSON, or Access service tokens.

## Secrets and Configuration Boundaries

Keep local only on Bob or in Cloudflare:

- Tunnel tokens managed by Cloudflare
- Access org tokens or service tokens
- Real `.env` values such as `HERMES_UI_PUBLIC_URL=https://hermes-ui.strategistudio.no`

Tracked in repo:

- `.env.example` placeholders only
- Documentation without secret values

Never commit or paste into Notion:

- Tunnel credential JSON contents
- Access service tokens
- API tokens
- Private keys
- Real `.env` contents

## Post-Go-Live Local Setting

Set on Bob only, not in git:

```text
HERMES_UI_PUBLIC_URL=https://hermes-ui.strategistudio.no
```

Update Bob LaunchAgent environment or local `.env` if the app needs the public URL at runtime.

## Related Documents

- `docs/architecture/deployment.md` — Bob LaunchAgent and local binding
- `docs/security/README.md` — security gates and secret handling
- `.planning/phases/04-cloudflare-access-tunnel/04-PLAN.md` — phase execution record
