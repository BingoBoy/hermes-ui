# Requirements: Hermes UI for Bob

**Defined:** 2026-06-03
**Core Value:** Truls can safely see whether Bob and Hermes are healthy without exposing shell access, secrets, or unsafe service controls.

## v1 Requirements

Requirements for the initial read-only release. Each maps to roadmap phases.

### Project Grounding

- [ ] **PROJ-01**: Project planning documents use `docs/notion/` as authoritative context.
- [ ] **PROJ-02**: Project workflow follows original GSD master flow: discuss -> plan -> execute -> verify.
- [ ] **PROJ-03**: The MVP scope explicitly excludes free terminal and arbitrary command execution.

### Runtime

- [ ] **RUN-01**: Hermes UI can run locally on Bob / Mac Mini M4.
- [ ] **RUN-02**: Hermes UI binds to `127.0.0.1:8787` by default.
- [ ] **RUN-03**: Runtime configuration is documented through `.env.example`.
- [ ] **RUN-04**: Real `.env` files remain ignored and uncommitted.

### Read-Only API

- [ ] **API-01**: `GET /api/status` returns Hermes UI service status, service name, version, and host.
- [ ] **API-02**: `GET /api/hermes/status` returns read-only Hermes gateway status without starting, stopping, or restarting Hermes.
- [ ] **API-03**: `GET /api/system` returns safe system information such as hostname, uptime, disk usage, and memory usage.
- [ ] **API-04**: API responses are structured JSON with safe error responses.

### Dashboard

- [ ] **UI-01**: Dashboard displays Hermes UI status.
- [ ] **UI-02**: Dashboard displays Bob / Mac Mini system status.
- [ ] **UI-03**: Dashboard displays Hermes gateway status.
- [ ] **UI-04**: Dashboard does not present enabled start, stop, restart, or terminal controls in v1.

### Security

- [ ] **SEC-01**: Browser users cannot submit arbitrary shell commands.
- [ ] **SEC-02**: Backend does not expose a generic command execution endpoint.
- [ ] **SEC-03**: UI and API do not expose secrets, API keys, tokens, passwords, private keys, or Cloudflare credentials.
- [ ] **SEC-04**: External access design assumes Cloudflare Tunnel plus Cloudflare Access.

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Logs

- **LOGS-01**: User can view recent Hermes logs after actual log paths are verified.
- **LOGS-02**: Log output is sanitized before display.
- **LOGS-03**: User can choose a bounded number of log lines such as 50, 100, or 500.

### Service Actions

- **ACT-01**: User can start Hermes through a verified approved command.
- **ACT-02**: User can stop Hermes through a verified approved command.
- **ACT-03**: User can restart Hermes through a verified approved command.
- **ACT-04**: Write actions are audited and require explicit confirmation.

### Operations

- **OPS-01**: Cloudflare Tunnel status is displayed when tunnel details are verified.
- **OPS-02**: LaunchAgent details are displayed when the plist and label are verified.
- **OPS-03**: Docker status is displayed if Docker becomes relevant for Hermes or adjacent services.

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Free terminal in browser | Creates unnecessary remote-control risk |
| Arbitrary command execution API | Violates the safe control-panel model |
| Start/stop/restart in v1 | Commands are not fully verified yet |
| Raw log display in v1 | Log paths and redaction model must be verified first |
| Direct public binding | Cloudflare Tunnel and Access should front external access |
| Advanced user management | Cloudflare Access handles external auth for MVP |
| Historical database | Not needed for first read-only status value |
| Full agent orchestration | Outside MVP and higher risk |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| PROJ-01 | Phase 1 | Complete |
| PROJ-02 | Phase 1 | Complete |
| PROJ-03 | Phase 1 | Complete |
| RUN-01 | Phase 1 | Complete |
| RUN-02 | Phase 1 | Complete |
| RUN-03 | Phase 1 | Complete |
| RUN-04 | Phase 1 | Complete |
| API-01 | Phase 1 | Complete |
| API-02 | Phase 1 | Complete |
| API-03 | Phase 1 | Complete |
| API-04 | Phase 1 | Complete |
| UI-01 | Phase 1 | Complete |
| UI-02 | Phase 1 | Complete |
| UI-03 | Phase 1 | Complete |
| UI-04 | Phase 1 | Complete |
| SEC-01 | Phase 1 | Complete |
| SEC-02 | Phase 1 | Complete |
| SEC-03 | Phase 1 | Complete |
| SEC-04 | Phase 1 | Complete |

**Coverage:**
- v1 requirements: 19 total
- Mapped to phases: 19
- Unmapped: 0

---
*Requirements defined: 2026-06-03*
*Last updated: 2026-06-03 after Phase 1 verification*
