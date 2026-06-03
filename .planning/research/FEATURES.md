# Feature Research: Hermes UI for Bob

## Table Stakes for v1

- General backend status via `GET /api/status`.
- Hermes gateway status via `GET /api/hermes/status`.
- Basic Bob system information via `GET /api/system`.
- Dashboard that presents read-only status clearly.
- Local-only binding to `127.0.0.1:8787`.
- Secret-safe responses and UI output.
- `.env.example` as the only tracked environment template.

## Deferred but Expected

- Hermes logs view after log paths are verified.
- Start, stop, and restart actions after exact `launchctl` commands are verified.
- Cloudflare Tunnel and Access setup verification.
- Audit log for write actions when write actions are introduced.
- More detailed launchctl, Docker, and Cloudflare tunnel status.

## Anti-Features

- Free terminal in the browser.
- Arbitrary shell command endpoint.
- Direct public network binding.
- Committing real `.env`.
- Logging tokens, passwords, private keys, Cloudflare secrets, or API keys.

## Complexity Notes

- Status and system information are low-risk if implemented read-only and sanitized.
- Hermes status is medium-risk because it may require local process or `launchctl` inspection.
- Logs are medium-risk because secret redaction must be reliable.
- Service control actions are high-risk and must wait for verified commands, confirmation UX, and audit logging.
