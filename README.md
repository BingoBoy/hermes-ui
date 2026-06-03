# Hermes UI

Et sikkert webbasert kontrollpanel for Hermes/Bob på Mac Mini M4.

## Mål

Hermes UI skal kjøre lokalt på Bob, lytte på `127.0.0.1:8787`, og senere eksponeres sikkert via Cloudflare Access.

## Første MVP

Første versjon skal være read-only:

- Status for Hermes UI
- Status for Bob/Mac Mini
- Status for Hermes gateway
- Enkel systeminformasjon

Start/stopp/restart av Hermes skal ikke implementeres før LaunchAgent og loggbaner er verifisert.

## Bob LaunchAgent-drift

Hermes UI kjører som LaunchAgent på Bob (`Truls-sin-Mac-mini.local`).

| Felt | Verifisert verdi |
|------|------------------|
| Label | `no.truls.hermes-ui` |
| Plist | `/Users/trulsdahl/Library/LaunchAgents/no.truls.hermes-ui.plist` |
| Working directory | `/Users/trulsdahl/Dev/hermes-ui` |
| Bind | `127.0.0.1:8787` |
| Prosess | `uvicorn backend.main:app` via `.venv` |

### Start, stopp og restart

Kjør på Bob som bruker `trulsdahl`:

```bash
# Start
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/no.truls.hermes-ui.plist

# Stopp
launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/no.truls.hermes-ui.plist

# Restart
launchctl kickstart -k gui/$(id -u)/no.truls.hermes-ui
```

### Sjekk status

```bash
# LaunchAgent-status
launchctl list | grep hermes-ui

# Port og prosess
lsof -nP -iTCP:8787 -sTCP:LISTEN

# API-status
curl -s http://127.0.0.1:8787/api/status | python3 -m json.tool
```

Forventet API-svar inkluderer `"status": "ok"`, `"read_only": true`, og `"allow_unsafe_commands": false`.

### Les Hermes UI-logger

LaunchAgent skriver til:

```text
/Users/trulsdahl/.hermes-ui/logs/hermes-ui.log
/Users/trulsdahl/.hermes-ui/logs/hermes-ui.error.log
```

Eksempler:

```bash
tail -n 100 ~/.hermes-ui/logs/hermes-ui.log
tail -n 100 ~/.hermes-ui/logs/hermes-ui.error.log
```

Se `docs/architecture/deployment.md` for full drift- og sikkerhetsmodell.

## Lokal kjøring (utvikling)

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
uvicorn backend.main:app --host 127.0.0.1 --port 8787
```

Åpne deretter:

```text
http://127.0.0.1:8787
```

## API

Read-only endepunkter:

```text
GET /api/status
GET /api/system
GET /api/hermes/status
GET /api/logs/sources
GET /api/logs/{source_id}?lines=100
```

Eksempler:

```text
GET /api/logs/gateway_stdout?lines=50
GET /api/logs/gateway_stderr?lines=50
```

Ingen start/stopp/restart-, terminal- eller shell-endepunkter finnes. Loggvisning bruker kun server-side allowlist.

## Konfigurasjon

Bruk `.env.example` som mal hvis lokale miljøvariabler trengs på Bob. Ekte `.env` skal holdes lokalt og er ignorert av git.

Viktige defaults:

```text
HERMES_UI_HOST=127.0.0.1
HERMES_UI_PORT=8787
ALLOW_UNSAFE_COMMANDS=false
```

## Verifisering

```bash
python -m compileall backend tests
python -m pytest
curl http://127.0.0.1:8787/api/status
curl http://127.0.0.1:8787/api/system
curl http://127.0.0.1:8787/api/hermes/status
curl http://127.0.0.1:8787/api/logs/sources
curl "http://127.0.0.1:8787/api/logs/gateway_stdout?lines=50"
curl "http://127.0.0.1:8787/api/logs/gateway_stderr?lines=50"
```

Serveren skal startes med `--host 127.0.0.1 --port 8787`.
