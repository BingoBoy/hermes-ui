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

Start/stopp av Hermes Gateway er fortsatt begrenset. **Restart** er implementert i Phase 5A, men krever `ALLOW_SERVICE_ACTIONS=true` på serveren.

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

Forventet API-svar inkluderer `"status": "ok"`, `"read_only": true`, `"allow_service_actions": false`, og `"allow_unsafe_commands": false`.

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

Allowlistede write-endepunkter:

```text
POST /api/hermes/restart   # Phase 5A — krever ALLOW_SERVICE_ACTIONS=true
POST /api/bob/tasks        # Phase 5C — krever ALLOW_BOB_TASKS=true
GET /api/bob/tasks         # Phase 5D — read-only, krever ALLOW_BOB_TASKS=true
GET /api/bob/tasks/{id}    # Phase 5D — read-only, krever ALLOW_BOB_TASKS=true
```

Eksempler:

```text
GET /api/logs/gateway_stdout?lines=50
GET /api/logs/gateway_stderr?lines=50
```

Ingen start/stop-, terminal- eller shell-endepunkter finnes. Restart bruker fast `launchctl kickstart` uten klient-input. Loggvisning bruker kun server-side allowlist.

Se `docs/api/service-actions.md` for audit, cooldown og feilhåndtering.

## Konfigurasjon

Bruk `.env.example` som mal hvis lokale miljøvariabler trengs på Bob. Ekte `.env` skal holdes lokalt og er ignorert av git.

Viktige defaults:

```text
HERMES_UI_HOST=127.0.0.1
HERMES_UI_PORT=8787
ALLOW_UNSAFE_COMMANDS=false
ALLOW_SERVICE_ACTIONS=false
ALLOW_BOB_TASKS=false
```

### Aktivere gateway restart på Bob

Legg i lokal `.env` på Bob (ikke commit):

```text
ALLOW_SERVICE_ACTIONS=true
```

Restart Hermes UI LaunchAgent etter endring. Dashboard viser **Restart Gateway**-knapp med bekreftelsesmodal.

Audit-logg:

```text
/Users/trulsdahl/.hermes-ui/logs/service-actions.log
```

Test lokalt:

```bash
curl -s -X POST http://127.0.0.1:8787/api/hermes/restart
# Forvent 403 når ALLOW_SERVICE_ACTIONS=false

curl -s -X POST http://127.0.0.1:8787/api/bob/tasks \
  -H 'Content-Type: application/json' \
  -d '{"title":"Test","body":"Safe test"}'
# Forvent 403 når ALLOW_BOB_TASKS=false

curl -s http://127.0.0.1:8787/api/bob/tasks?limit=20
curl -s http://127.0.0.1:8787/api/bob/tasks/t_79f256ed
# Forvent 403 når ALLOW_BOB_TASKS=false
```

### Aktivere Bob-oppgaver på Bob

Legg i lokal `.env` på Bob (ikke commit):

```text
ALLOW_BOB_TASKS=true
HERMES_CLI_BIN=/Users/trulsdahl/.hermes/hermes-agent/venv/bin/hermes
```

Restart Hermes UI LaunchAgent. Dashboard viser **Bob task-maler** (valgfrie felt per mal + «Send mal til Bob»), **Send oppgave til Bob**, **Bob-oppgaver** (med valgfri auto-oppdatering), **Bob Inbox** (kopier resultat/ID, vis mer) og trygge resultathandlinger i oppgavedetaljer når gaten er på.

Audit-logg:

```text
/Users/trulsdahl/.hermes-ui/logs/bob-interactions.log
```

## Tester

Kjør fra prosjektroten med prosjektets venv (ikke system-`python3` uten pytest):

```bash
source .venv/bin/activate
python -m pytest
```

Uten aktivert venv:

```bash
.venv/bin/python -m pytest
```

`pytest.ini` setter `pythonpath = .` slik at `backend` importeres riktig — også når du kjører `.venv/bin/pytest` direkte.

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
