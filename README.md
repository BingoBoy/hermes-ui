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

## Lokal kjøring

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

Første MVP eksponerer kun read-only endepunkter:

```text
GET /api/status
GET /api/system
GET /api/hermes/status
```

Ingen start/stopp/restart-, logg-, terminal- eller shell-endepunkter finnes i denne fasen.

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
```

Serveren skal startes med `--host 127.0.0.1 --port 8787`.
