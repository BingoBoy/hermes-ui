# Stack Research: Hermes UI for Bob

## Recommendation

Use a small API-first web stack for the first MVP:

- Backend: FastAPI or Flask, with a strong preference for FastAPI if the API contract becomes the primary surface.
- Frontend: Start simple and avoid a heavy UI framework until the backend and security model are verified.
- Runtime: Local service on Bob / Mac Mini M4, bound to `127.0.0.1:8787`.
- External access: Cloudflare Tunnel plus Cloudflare Access.
- Configuration: `.env.example` in git, real `.env` local-only and ignored.

## Why This Stack Fits

The project is an operational dashboard, not a general web product. The important constraints are local binding, explicit endpoints, safe output handling, and a small surface area. A minimal backend plus simple UI keeps the MVP auditable.

## Stack Boundaries

- Do not implement a browser terminal.
- Do not build a command runner abstraction before approved commands are verified.
- Do not expose the backend on `0.0.0.0`.
- Do not add authentication inside the MVP unless Cloudflare Access is unavailable.
- Do not introduce a database for v1 read-only status.

## Confidence

High. The recommendation follows the project documentation in `docs/notion/03 Teknisk arkitektur...`, `docs/notion/04 API-spesifikasjon...`, and the read-only MVP direction in `README.md`.
