# Architecture Research: Hermes UI for Bob

## Target Architecture

```text
Client device
  -> Cloudflare Access
  -> Cloudflare Tunnel
  -> Bob / Mac Mini M4
  -> Hermes UI on 127.0.0.1:8787
  -> read-only local status checks
```

## Components

### Hermes UI Backend

The backend exposes a small set of explicit HTTP endpoints. In v1, these endpoints are read-only:

- `GET /api/status`
- `GET /api/hermes/status`
- `GET /api/system`

Later endpoints for logs and service actions should be added only after log paths and commands are verified.

### Dashboard UI

The first UI should act like an operational control panel:

- Bob status card
- Hermes status card
- System info card
- Clear warning or disabled state for unavailable write actions

### Bob Runtime

Bob is the source of truth for local service state. Hermes appears to be managed by launchctl through the `ai.hermes.gateway` LaunchAgent, but command details must be confirmed before use.

### Cloudflare Edge

Cloudflare Tunnel provides the route into Bob. Cloudflare Access provides authentication and authorization for external access.

## Data Flow

1. Browser requests dashboard.
2. Dashboard fetches read-only API endpoints.
3. Backend reads safe local status sources.
4. Backend returns sanitized JSON.
5. Browser renders status without exposing shell output beyond approved fields.

## Suggested Build Order

1. Preserve and document the safety contract.
2. Build local read-only backend.
3. Build dashboard for the read-only endpoints.
4. Verify local binding and status accuracy on Bob.
5. Add Cloudflare Access exposure.
6. Plan logs and write actions only after verification.
