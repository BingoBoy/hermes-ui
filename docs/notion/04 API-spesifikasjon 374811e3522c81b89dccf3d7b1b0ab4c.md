# 04 API-spesifikasjon

# Formål

Denne siden beskriver første API-spesifikasjon for Hermes UI for Bob.

# Prinsipp

API-et skal være lite, eksplisitt og trygt. Hvert endepunkt skal gjøre én tydelig ting.

# Endepunkter

## GET /api/status

Returnerer generell status for UI-backend.

Eksempelrespons:

```json
{
  "status": "ok",
  "service": "hermes-ui",
  "version": "0.1.0",
  "host": "Bob"
}
```

## GET /api/hermes/status

Returnerer om Hermes kjører.

Eksempelrespons:

```json
{
  "service": "hermes",
  "running": true,
  "pid": 12345,
  "last_checked": "2026-06-03T12:00:00+02:00"
}
```

## POST /api/hermes/start

Starter Hermes via godkjent kommando.

Eksempelrespons:

```json
{
  "action": "start",
  "success": true,
  "message": "Hermes start command executed"
}
```

## POST /api/hermes/stop

Stopper Hermes via godkjent kommando.

Eksempelrespons:

```json
{
  "action": "stop",
  "success": true,
  "message": "Hermes stop command executed"
}
```

## POST /api/hermes/restart

Restarter Hermes via godkjent kommando.

Eksempelrespons:

```json
{
  "action": "restart",
  "success": true,
  "message": "Hermes restart command executed"
}
```

## GET /api/logs/hermes?lines=100

Returnerer siste logglinjer fra Hermes.

Eksempelrespons:

```json
{
  "service": "hermes",
  "lines": 100,
  "log": [
    "line 1",
    "line 2"
  ]
}
```

## GET /api/system

Returnerer enkel systemstatus.

Eksempelrespons:

```json
{
  "hostname": "Bob",
  "uptime": "3 days, 04:12",
  "disk_usage": "42%",
  "memory_usage": "61%"
}
```

# Feilhåndtering

Alle feil bør returnere strukturert JSON.

```json
{
  "success": false,
  "error": "Command failed",
  "details": "Short safe explanation"
}
```

# Sikkerhetsregler

- API-et skal ikke ta imot vilkårlige shell-kommandoer
- Alle handlinger skal være hardkodet eller definert i en allowlist
- Output skal renses for secrets
- POST-handlinger bør loggføres
- Cloudflare Access skal beskytte ekstern tilgang

# Kommando-allowlist

Før implementering må disse fylles ut basert på faktisk Hermes-oppsett på Bob:

```
hermes_status_command=""
hermes_start_command=""
hermes_stop_command=""
hermes_restart_command=""
hermes_log_path=""
```