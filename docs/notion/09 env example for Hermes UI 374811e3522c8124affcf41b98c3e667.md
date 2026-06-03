# 09 .env.example for Hermes UI

# Formål

Denne siden inneholder en foreslått `.env.example` for Hermes UI.

Dette er ikke en ekte `.env`-fil. Den inneholder bare variabelnavn og tomme eksempelverdier.

Ekte `.env` skal ligge lokalt på Bob og skal ikke committes til GitHub eller limes inn i Notion.

# Anbefalt filnavn

```
.env.example
```

# Anbefalt `.gitignore`

```
.env
.env.local
.env.*.local
*.pem
*.key
cloudflared/*.json
```

# .env.example

```bash
# ============================================================
# Hermes UI for Bob - example environment file
# Copy this file to .env on Bob and fill in real local values.
# Never commit the real .env file.
# ============================================================

# ------------------------------------------------------------
# App
# ------------------------------------------------------------
HERMES_UI_ENV=development
HERMES_UI_HOST=127.0.0.1
HERMES_UI_PORT=8787
HERMES_UI_PUBLIC_URL=
HERMES_UI_LOG_LEVEL=info

# ------------------------------------------------------------
# Bob / Mac Mini M4
# ------------------------------------------------------------
BOB_HOSTNAME=
BOB_LOCAL_HOSTNAME=
BOB_LOCAL_IP=
BOB_SSH_USER=
BOB_SSH_ALIAS=

# ------------------------------------------------------------
# Hermes commands
# Use exact approved commands only.
# Do not expose arbitrary shell commands in the UI.
# ------------------------------------------------------------
HERMES_STATUS_COMMAND=
HERMES_START_COMMAND=
HERMES_STOP_COMMAND=
HERMES_RESTART_COMMAND=
HERMES_WORKDIR=
HERMES_LOG_FILE=

# ------------------------------------------------------------
# launchctl / service management
# Fill in if Hermes is managed by launchctl.
# ------------------------------------------------------------
HERMES_LAUNCHD_LABEL=
HERMES_LAUNCHD_PLIST=

# ------------------------------------------------------------
# Docker
# Fill in only if Hermes or related services run in Docker.
# ------------------------------------------------------------
HERMES_DOCKER_COMPOSE_FILE=
HERMES_DOCKER_SERVICE=

# ------------------------------------------------------------
# Cloudflare Tunnel / Access
# Do not place Cloudflare credentials JSON in this file.
# Document path only if needed.
# ------------------------------------------------------------
CLOUDFLARE_TUNNEL_NAME=
CLOUDFLARE_TUNNEL_ID=
CLOUDFLARE_TUNNEL_CONFIG_PATH=
CLOUDFLARE_ACCESS_AUDIENCE=
CLOUDFLARE_ACCESS_TEAM_DOMAIN=

# ------------------------------------------------------------
# LM Studio / local model API
# Only needed if Hermes UI or Hermes talks directly to LM Studio.
# ------------------------------------------------------------
LM_STUDIO_ENABLED=false
LM_STUDIO_BASE_URL=http://127.0.0.1:1234/v1
LM_STUDIO_MODEL=

# ------------------------------------------------------------
# n8n / other local services
# Optional for later phases.
# ------------------------------------------------------------
N8N_ENABLED=false
N8N_LOCAL_URL=http://127.0.0.1:5678
PAAPP_ENABLED=false
PAAPP_LOCAL_URL=

# ------------------------------------------------------------
# Security
# Optional shared secret for local API calls if needed.
# Prefer Cloudflare Access for external protection.
# ------------------------------------------------------------
HERMES_UI_API_TOKEN=
ALLOW_UNSAFE_COMMANDS=false

# ------------------------------------------------------------
# Logging
# ------------------------------------------------------------
HERMES_UI_AUDIT_LOG=
HERMES_UI_MAX_LOG_LINES=500
```

# Kommentar om tokens og passord

Hvis det senere trengs tokens, bør de håndteres på én av disse måtene:

## Alternativ A – `.env`

Enkelt og praktisk for MVP.

Brukes når:

- Løsningen bare kjører lokalt på Bob
- `.env` er i `.gitignore`
- Filrettigheter settes strengt

Eksempel:

```bash
chmod 600 .env
```

## Alternativ B – macOS Keychain

Bedre for ekstra sensitive verdier.

Brukes når:

- Scripts trenger tokens
- Du vil unngå tokens i tekstfiler
- Verdien kan hentes med `security find-generic-password`

Eksempel på uthenting:

```bash
security find-generic-password -a "$USER" -s "hermes-ui-api-token" -w
```

## Anbefaling for MVP

Start med `.env.example` i repoet og ekte `.env` lokalt på Bob.

Flytt eventuelt enkelte secrets til macOS Keychain senere hvis løsningen får flere integrasjoner eller høyere sikkerhetsbehov.