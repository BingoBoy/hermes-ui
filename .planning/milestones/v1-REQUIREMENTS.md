# Requirements Archive: v1 (Safe Operations Dashboard)

**Shipped:** 2026-06-04  
**Scope:** ROADMAP phases 1–6. Replaces `.planning/REQUIREMENTS.md` at milestone close.

## v1 Requirements — all complete

### Project Grounding

- [x] **PROJ-01**: Project planning documents use `docs/notion/` as authoritative context.
- [x] **PROJ-02**: Project workflow follows original GSD master flow: discuss -> plan -> execute -> verify.
- [x] **PROJ-03**: The MVP scope explicitly excludes free terminal and arbitrary command execution.

### Runtime

- [x] **RUN-01**: Hermes UI can run locally on Bob / Mac Mini M4.
- [x] **RUN-02**: Hermes UI binds to `127.0.0.1:8787` by default.
- [x] **RUN-03**: Runtime configuration is documented through `.env.example`.
- [x] **RUN-04**: Real `.env` files remain ignored and uncommitted.

### Read-Only API

- [x] **API-01**: `GET /api/status` returns Hermes UI service status, service name, version, and host.
- [x] **API-02**: `GET /api/hermes/status` returns read-only Hermes gateway status without starting, stopping, or restarting Hermes.
- [x] **API-03**: `GET /api/system` returns safe system information such as hostname, uptime, disk usage, and memory usage.
- [x] **API-04**: API responses are structured JSON with safe error responses.

### Dashboard

- [x] **UI-01**: Dashboard displays Hermes UI status.
- [x] **UI-02**: Dashboard displays Bob / Mac Mini system status.
- [x] **UI-03**: Dashboard displays Hermes gateway status.
- [x] **UI-04**: Dashboard does not present enabled start, stop, restart, or terminal controls in v1.

### Security

- [x] **SEC-01**: Browser users cannot submit arbitrary shell commands.
- [x] **SEC-02**: Backend does not expose a generic command execution endpoint.
- [x] **SEC-03**: UI and API do not expose secrets, API keys, tokens, passwords, private keys, or Cloudflare credentials.
- [x] **SEC-04**: External access design assumes Cloudflare Tunnel plus Cloudflare Access.

## v2 requirements — outcomes at v1 close

| ID | Outcome | Phase |
|----|---------|-------|
| LOGS-01–03 | **Satisfied** | 2 |
| ACT-03 restart | **Satisfied** | 5A |
| ACT-04 audit + confirm | **Satisfied** | 5A |
| ACT-01 start | **Deferred** | 5B — maintenance-window live verify |
| ACT-02 stop | **Deferred** | 5B |
| OPS-02 LaunchAgent details | **Satisfied** | 6 |
| OPS-03 Docker | **Satisfied** | 6 (off on Bob) |
| OPS-01 Tunnel status in UI | **Backlog** | 4 docs only |

## Traceability (final)

| Requirement | Phase | Status |
|-------------|-------|--------|
| PROJ-01–03, RUN-01–04, API-01–04, UI-01–04, SEC-01–04 | Phase 1 | Complete |
| LOGS-01–03 | Phase 2 | Complete |

## Known gaps at close (accepted tech debt)

- 5B start/stop not implemented
- OPS-01 no live tunnel status card
- Bob worker `hermes-assignee` — external ops (v2.1-bob-ux track)

---
*Archived: /gsd-complete-milestone v1 — 2026-06-04*
