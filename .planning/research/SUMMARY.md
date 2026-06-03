# Research Summary: Hermes UI for Bob

## Stack

Build a small local web control panel that listens only on `127.0.0.1:8787`. Use a minimal backend, preferably FastAPI if the project stays API-first, with a simple dashboard UI. External access should come through Cloudflare Tunnel and Cloudflare Access.

## Table Stakes

- Read-only backend status.
- Read-only Hermes gateway status.
- Read-only Bob system information.
- Dashboard that makes current health obvious.
- No free terminal or arbitrary commands.
- `.env.example` tracked; real `.env` ignored.
- Later Cloudflare Access protection for external usage.

## Watch Out For

- Do not implement start, stop, or restart until `launchctl` commands and log paths are verified.
- Do not expose raw shell output or logs without redaction.
- Do not bind the app to `0.0.0.0`.
- Do not mix old Mac Mini tunnel/service facts with Bob / Mac Mini M4.
- Do not treat Cloudflare Tunnel as sufficient without Cloudflare Access.

## Planning Implication

The roadmap should begin with read-only safety and environment verification, then build the local status API, then the dashboard, then verify Cloudflare exposure. Write actions and logs belong in later gated phases.

---
*Research synthesized: 2026-06-03 from `docs/notion/`*
