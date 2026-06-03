# 07 Bob/Mac Mini M4 – eksisterende oppsett og avhengigheter

# Formål

Denne siden samler relevant informasjon fra den eksisterende Notion-siden **Ny Mac Mini M4 – Hermes/Bob, SSH og Cloudflare Tunnel**, slik at Hermes UI-prosjektet har nødvendig kontekst uten at Truls må lete frem alt på nytt.

# Kilde

Informasjonen er hentet fra Notion-siden:

**Ny Mac Mini M4 – Hermes/Bob, SSH og Cloudflare Tunnel**

Denne siden ligger under hovedsiden **Mac Mini Server**.

# Maskinrolle

## Ny Mac Mini M4

Anbefalt rolle: **fast lokal AI- og servermaskin**.

Maskinen skal kunne brukes til:

- Hermes/Bob
- LM Studio og lokale modeller
- Docker-baserte tjenester
- Cloudflare Tunnel
- Lokale API-er og automasjoner
- Eventuelt n8n, PAapp, Markedsstrategi-app og andre interne tjenester

## MacBook Pro M1

Anbefalt rolle: **daglig arbeidsmaskin**.

Brukes til:

- Cursor
- Nettleser og ChatGPT
- SSH inn til Mac Mini M4
- Lett utvikling og administrasjon
- Dokumentasjon og vanlig kontorarbeid

## Gammel Mac Mini

Anbefalt rolle: **sekundær maskin / historisk oppsett / test**.

Gammel Mac Mini og ny Mac Mini skal dokumenteres separat slik at serveroppsettene ikke blandes.

# Overordnet arkitektur for Hermes UI

```
MacBook Pro / iPhone / iPad
  ↓ HTTPS
Cloudflare Access
  ↓ Cloudflare Tunnel
Ny Mac Mini M4 / Bob
  ├─ Hermes/Bob
  ├─ Hermes UI
  ├─ LM Studio
  ├─ Docker
  ├─ cloudflared
  └─ lokale API-er/automasjoner
```

# Relevante prinsipper fra eksisterende serveroppsett

- MacBook skal være klient/arbeidsflate.
- Mac Mini M4 skal være fast server/agentmaskin.
- Cloudflare Tunnel skal brukes fremfor port forwarding i ruteren.
- Cloudflare Access skal brukes foran interne tjenester.
- Interne tjenester skal ikke eksponeres åpent på internett.
- API-nøkler, tokens, passord og `.env`-innhold skal ikke legges i Notion.
- Dokumentasjon i Notion skal beskrive hvor hemmeligheter ligger, ikke hva de inneholder.

# Cloudflare Tunnel

Anbefalt praksis fra serverdokumentasjonen:

- Bruk egen Cloudflare Tunnel for ny Mac Mini M4.
- Ikke bland ny Mac Mini M4 med gammel Mac Mini-tunnel.
- Bruk tydelige tunnelnavn.

Foreslåtte tunnelnavn:

```
gammel-mac-mini-tunnel
mac-mini-m4-tunnel
```

Mulige subdomener:

```
bob.<domene>
lmstudio.<domene>
n8n.<domene>
paapp.<domene>
status.<domene>
```

For Hermes UI kan et eget subdomene vurderes:

```
hermes.<domene>
bob-ui.<domene>
hermes-ui.<domene>
```

# Sikkerhetsregler

Tjenester som bør beskyttes med Cloudflare Access / Zero Trust:

- Hermes/Bob
- Hermes UI
- LM Studio API
- n8n
- interne dashboards
- lokale API-er
- SSH

Viktige regler:

- Ikke åpne porter direkte i ruteren hvis det kan unngås.
- Ikke eksponer LM Studio API uten autentisering/Access.
- Begrens SSH-tilgang til riktig bruker.
- Bruk SSH-nøkler der det er mulig.
- Ikke legg `.env`, API-nøkler eller passord i Notion.

# Kjente lokale tjenester og porter

Fra eksisterende dokumentasjon:

| Tjeneste | Port | Lokal URL | Cloudflare URL | Access-beskyttet |
| --- | --- | --- | --- | --- |
| --- | ---: | --- | --- | --- |
| Hermes/Bob | TBD | TBD | TBD | Ja |
| Hermes UI | foreslått 8787 | [http://127.0.0.1:8787](http://127.0.0.1:8787) | TBD | Ja |
| LM Studio | 1234 | [http://127.0.0.1:1234](http://127.0.0.1:1234) | TBD | Ja |
| n8n | 5678 | [http://127.0.0.1:5678](http://127.0.0.1:5678) | TBD | Ja |
| PAapp | TBD | TBD | TBD | Ja |

# LM Studio-status fra eksisterende dokumentasjon

Det finnes statuslogg for LM Studio / llmster på ny Mac Mini M4.

Kjente punkter:

- `lms` fungerer når `/Users/trulsdahl/.lmstudio/bin` legges i `PATH`.
- `llmster` daemon starter korrekt.
- Lokal OpenAI-kompatibel API på port `1234` svarte ikke ennå i den dokumenterte testen.
- Dette betyr trolig at daemon kjører, men at modellserver/API-server ikke er startet eller at ingen modell er lastet inn.

Dokumenterte kommandoer:

```bash
export PATH="/Users/trulsdahl/.lmstudio/bin:$PATH"
lms --version
lms daemon up
curl http://localhost:1234/v1/models
```

Neste feilsøkingskommandoer fra eksisterende dokumentasjon:

```bash
export PATH="/Users/trulsdahl/.lmstudio/bin:$PATH"
lms --help
lms daemon --help
lms server --help 2>/dev/null || true
lms model --help 2>/dev/null || true
lms status 2>/dev/null || true
lms ps 2>/dev/null || true
```

# SSH og administrasjon

Eksisterende dokumentasjon anbefaler SSH fra MacBook til ny Mac Mini M4.

Lokal test:

```bash
ssh truls@<lokal-ip>
```

Anbefalt SSH-alias:

```
Host macmini-m4
    HostName <lokal-ip>
    User truls
    AddKeysToAgent yes
    UseKeychain yes
```

For Hermes UI bør faktisk SSH-alias, bruker og host dokumenteres, men ikke private nøkler.

# Relevans for Hermes UI

Hermes UI bør bygges med følgende forutsetninger:

- Kjører på Bob / ny Mac Mini M4.
- Lytter lokalt på `127.0.0.1`, ikke åpent nettverksinterface.
- Eksponeres via Cloudflare Tunnel.
- Beskyttes med Cloudflare Access.
- Bruker lokale kommandoer og allowlist for Hermes-operasjoner.
- Leser logger lokalt fra Bob.
- Har `.env.example` i repoet, men ekte `.env` holdes lokalt og skal ikke committes.

# Avklaringer som fortsatt må fylles inn

- Faktisk maskinnavn/hostname for Bob
- Faktisk lokal IP
- Faktisk SSH-bruker
- Faktisk SSH-alias som skal brukes
- Faktisk Cloudflare Tunnel-navn
- Faktisk subdomene for Hermes UI
- Hvordan Hermes startes/stoppes/restartes i dag
- Hvor Hermes-loggene ligger
- Om Hermes kjører via launchctl, Docker, shell-script eller annet
- Om LM Studio skal være en direkte avhengighet i første MVP