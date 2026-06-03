# Pitfalls Research: Hermes UI for Bob

## Critical Pitfalls

### Accidentally Creating Remote Shell Access

Warning sign: Generic command parameters, "run command" endpoints, or UI fields that accept shell input.

Prevention: Only expose explicit, named capabilities. Keep the first MVP read-only.

### Enabling Service Controls Too Early

Warning sign: Start, stop, or restart buttons appear before launchctl behavior and log paths are verified.

Prevention: Treat service controls as v2/gated scope. Document verified commands first, then plan write actions separately.

### Binding to a Public Interface

Warning sign: Server starts on `0.0.0.0` or a LAN address.

Prevention: Default to `127.0.0.1:8787` and test that the service is not reachable directly from the network.

### Leaking Secrets Through Logs or Environment Output

Warning sign: Raw log output, environment dumps, token-bearing Cloudflare paths, or full command output rendered in UI.

Prevention: Avoid logs in v1. When logs are added, sanitize tokens, passwords, API keys, private keys, and Cloudflare credentials.

### Confusing Old and New Mac Mini Context

Warning sign: Tunnel names, SSH aliases, or service paths copied from the old Mac Mini.

Prevention: Use Bob / Mac Mini M4 facts from `docs/notion/08 Dette trenger Truls å finne frem...` and verify locally.

### Treating Cloudflare Access as Optional

Warning sign: Public URL is exposed before Access policy is configured.

Prevention: Cloudflare exposure is not complete until Access protection is verified.

## Phase Mapping

- Phase 1 should address command, path, and environment verification.
- Phase 2 should enforce read-only API boundaries.
- Phase 3 should keep the UI from suggesting unavailable write actions.
- Phase 4 should verify local binding, Cloudflare Access, and secret-safety.
