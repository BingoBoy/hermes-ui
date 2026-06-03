# 08 Dette trenger Truls å finne frem

# Formål

Denne siden er en praktisk sjekkliste over informasjon Truls bør finne frem for at Hermes UI-dokumentasjonen og implementeringen skal bli presis.

Ikke lim inn passord, tokens eller hemmeligheter i Notion.

Sist oppdatert: 3. juni 2026. Verdiene under er hentet fra Notion-prosjektet, lokal SSH-konfigurasjon og direkte sjekk mot `BobRemote` der det var mulig.

# 1. Maskin og nettverk

Fyll inn eller finn frem:

| Felt | Verdi |
| --- | --- |
| Maskinnavn / hostname | `Truls-sin-Mac-mini.local` |
| LocalHostName | `Truls-sin-Mac-mini` |
| Lokal IP-adresse | `192.168.0.106` |
| Brukernavn på Bob | `trulsdahl` |
| SSH-alias fra MacBook | `Bob` lokalt, `BobRemote` via Cloudflare Access |
| Lokal SSH-host | `Truls-sin-Mac-mini.local` |
| Ekstern SSH-host | `bob-ssh.strategistudio.no` |
| Tilkobling | Ser ut som Ethernet via `en0` |
| DHCP-reservasjon i router | Ikke bekreftet |

Kommandoer som kan kjøres på Bob:

```bash
hostname
whoami
scutil --get LocalHostName
ipconfig getifaddr en0 2>/dev/null || true
ipconfig getifaddr en1 2>/dev/null || true
```

Fra MacBook:

```bash
ssh <ssh-alias> 'hostname && whoami && scutil --get LocalHostName'
```

# 2. Hermes/Bob

Finn frem:

| Felt | Verdi |
| --- | --- |
| Hvor Hermes er installert | `/Users/trulsdahl/.hermes/hermes-agent` |
| Hermes-binær | `/Users/trulsdahl/.local/bin/hermes` og `/Users/trulsdahl/.hermes/hermes-agent/venv/bin/hermes` |
| Kjører nå | Ja |
| Aktiv prosess | `/Users/trulsdahl/.hermes/hermes-agent/venv/bin/python -m hermes_cli.main gateway run --replace` |
| LaunchAgent | `ai.hermes.gateway` |
| LaunchAgent-fil | `/Users/trulsdahl/Library/LaunchAgents/ai.hermes.gateway.plist` |
| Kommando for å starte Hermes | Sannsynlig: `launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/ai.hermes.gateway.plist`. Bør verifiseres mot plist før UI kobles til. |
| Kommando for å stoppe Hermes | Sannsynlig: `launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/ai.hermes.gateway.plist`. Bør verifiseres mot plist før UI kobles til. |
| Kommando for å restarte Hermes | Sannsynlig: `launchctl kickstart -k gui/$(id -u)/ai.hermes.gateway`. Bør verifiseres mot plist før UI kobles til. |
| Kommando for å sjekke status | `launchctl list | grep -i hermes` eller `ps aux | grep -i '[h]ermes'` |
| Loggfil(er) | Ikke ferdig bekreftet. Sjekk under `~/.local/state/hermes`, `~/.hermes` og LaunchAgent-loggfeltene i plist. |
| Kjører via launchctl? | Ja |
| Kjører via Docker? | Ikke for gateway-prosessen som ble funnet |
| Kjører via shell-script? | Ikke som hoveddrift; gatewayen kjøres via Python/launchctl |

Nyttige kommandoer:

```bash
which hermes 2>/dev/null || true
hermes --help 2>/dev/null || true
launchctl list | grep -i hermes || true
ps aux | grep -i '[h]ermes' || true
find ~ -iname '*hermes*' -maxdepth 5 2>/dev/null | head -100
```

# 3. Cloudflare

Finn frem:

| Felt | Verdi |
| --- | --- |
| Cloudflare-konto / område | Cloudflare Zero Trust for `strategistudio.no` |
| Domene som skal brukes | `strategistudio.no` |
| Tunnelnavn | Ikke endelig valgt for Hermes UI. Historikk: `kokebok-web` og `n8ntunnel` har vært aktive; `macmini-tunnel` finnes, men har vært inaktiv. |
| Tunnel-ID | Ikke bekreftet for endelig Hermes UI-tunnel |
| Subdomene for Hermes UI | Anbefalt: `hermes.strategistudio.no` eller `hermes-ui.strategistudio.no` |
| Cloudflare Access-policy | Skal brukes. Anbefalt egen policy for Truls, samme mønster som `Only Truls` for andre interne apper. |

Nyttige kommandoer på Bob:

```bash
cloudflared --version
cloudflared tunnel list
cloudflared tunnel info <tunnel-navn-eller-id>
```

Ikke lim inn Cloudflare credentials i Notion.

# 4. Porter og lokale tjenester

Finn frem eller bestem:

| Tjeneste | Lokal port | Lokal URL | Ekstern URL | Access-beskyttet |
| --- | --- | --- | --- | --- |
| --- | ---: | --- | --- | --- |
| Hermes UI | 8787 | [http://127.0.0.1:8787](http://127.0.0.1:8787) | Anbefalt: `https://hermes.strategistudio.no` eller `https://hermes-ui.strategistudio.no` | Ja |
| Hermes/Bob | Ikke bekreftet som HTTP-port | Gateway kjører lokalt via launchctl/prosess, ikke som bekreftet webport | Ikke direkte eksponering i MVP | Ja, hvis eksponert senere |
| LM Studio | 1234 | [http://127.0.0.1:1234](http://127.0.0.1:1234) | TBD. Bør ikke eksponeres uten Cloudflare Access. | Ja |
| n8n | 5678 | [http://127.0.0.1:5678](http://127.0.0.1:5678) | Historikk: `n8n.strategistudio.no` via `n8ntunnel` | Ja |

Nyttige kommandoer:

```bash
lsof -nP -iTCP -sTCP:LISTEN
```

eller mer målrettet:

```bash
lsof -nP -iTCP:8787 -sTCP:LISTEN || true
lsof -nP -iTCP:1234 -sTCP:LISTEN || true
lsof -nP -iTCP:5678 -sTCP:LISTEN || true
```

# 5. LM Studio / lokale modeller

Finn frem:

| Felt | Verdi |
| --- | --- |
| Brukes i MVP? | Ikke nødvendig for første kontrollpanel-MVP, men tilgjengelig hvis UI-et senere skal ha assistent-/modellfunksjoner. |
| Lokal API-port | 1234 |
| Modellnavn | `qwen2.5-coder-7b-instruct` |
| Embedding-modell | `text-embedding-nomic-embed-text-v1.5` |
| API-base-url | [http://127.0.0.1:1234/v1](http://127.0.0.1:1234/v1) |
| Status på modellserver | Aktiv. `llmster` lytter på `127.0.0.1:1234`, og `lms status` viste server `ON`. |

Test:

```bash
export PATH="/Users/trulsdahl/.lmstudio/bin:$PATH"
lms status 2>/dev/null || true
lms ps 2>/dev/null || true
curl -sS http://127.0.0.1:1234/v1/models | jq
```

# 6. Secrets og miljøvariabler

Ikke send eller lim inn hemmeligheter i chat eller Notion.

Det som trengs i dokumentasjonen er:

- Hvilke variabler som finnes
- Hva de brukes til
- Hvor `.env` ligger lokalt
- Om de skal hentes fra `.env`, Keychain eller annet

Foreslåtte ikke-hemmelige verdier for `.env.example`:

```
HERMES_UI_HOST=127.0.0.1
HERMES_UI_PORT=8787
HERMES_INSTALL_DIR=/Users/trulsdahl/.hermes/hermes-agent
HERMES_LAUNCH_AGENT=ai.hermes.gateway
HERMES_LOCAL_USER=trulsdahl
HERMES_LOCAL_HOSTNAME=Truls-sin-Mac-mini.local
HERMES_LOCAL_IP=192.168.0.106
HERMES_EXTERNAL_SSH_HOST=bob-ssh.strategistudio.no
LM_STUDIO_BASE_URL=http://127.0.0.1:1234/v1
```

# Anbefaling

For MVP anbefales:

- Bruk `.env` lokalt på Bob for ikke-sensitive konfigurasjonsverdier og eventuelle tokens som ikke støttes av Keychain.
- Legg inn `.env.example` i repoet.
- Legg ekte `.env` i `.gitignore`.
- Vurder macOS Keychain for ekstra sensitive tokens hvis de skal brukes fra scripts.

# Ting som bør dokumenteres, men ikke deles

- API-nøkler
- Tokens
- Passord
- Private SSH-nøkler
- Cloudflare credentials-filer
- Innholdet i ekte `.env`