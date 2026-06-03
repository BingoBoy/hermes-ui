# Security Notes: Hermes UI for Bob

## Phase 1 Boundary

The first MVP is strictly read-only. It may show:

- Hermes UI service status
- Bob / Mac Mini M4 system information
- Hermes gateway status

It must not perform service control actions.

## Explicitly Not Implemented

The following capabilities are intentionally outside Phase 1:

- Start Hermes
- Stop Hermes
- Restart Hermes
- Log viewing
- Free terminal access in the browser
- Arbitrary shell command endpoints
- User-defined command execution
- Direct Cloudflare configuration
- Docker setup

## Network Boundary

Hermes UI defaults to:

```text
127.0.0.1:8787
```

Do not bind the service to `0.0.0.0` for the MVP. Later external access should go through Cloudflare Tunnel and Cloudflare Access.

## Environment and Secrets

`.env.example` is the tracked template. Real `.env` files must stay local and uncommitted.

Never commit or display:

- API keys
- Tokens
- Passwords
- Private SSH keys
- Cloudflare credentials
- Real `.env` contents

`ALLOW_UNSAFE_COMMANDS` must remain `false`.

## Read-Only Inspection

The backend may use fixed local inspection commands for status, such as process or launchctl checks. These commands must not be built from browser input or user-provided API parameters.

If Hermes cannot be checked, the API should return a safe status payload instead of failing open or exposing raw sensitive output.

## Gates Before Future Write Actions

Before adding start, stop, or restart:

1. Verify the exact `launchctl` commands on Bob.
2. Verify the LaunchAgent label and plist path.
3. Add explicit confirmation UX.
4. Add audit logging.
5. Keep actions allowlisted and fixed.
6. Re-run security verification.

Before adding logs:

1. Verify actual log paths.
2. Define redaction rules.
3. Bound the number of returned lines.
4. Ensure no secrets are exposed.

