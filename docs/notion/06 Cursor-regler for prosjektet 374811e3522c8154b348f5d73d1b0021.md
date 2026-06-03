# 06 Cursor-regler for prosjektet

# Formål

Denne siden beskriver anbefalte Cursor-regler for Hermes UI-prosjektet.

# Arbeidsflyt

Bruk original GSD Master-flyt:

```
/gsd-new-project
/gsd-map-codebase
/gsd-discuss-phase
/gsd-plan-phase
/gsd-execute-phase
/gsd-verify-work
```

Arbeidsrekkefølge:

```
discuss → plan → execute → verify
```

# Prinsipper

- Små planer
- 2–3 atomiske oppgaver per plan
- Én tydelig endring per commit
- Ikke bygg mer enn MVP-scope
- Ikke introduser fri shell i webgrensesnittet
- Ikke eksponer secrets
- Dokumenter kommandoer og paths før implementering
- Verifiser etter hver fase

# Kodestandard

- Les eksisterende filer før endring
- Endre minst mulig
- Hold backend-endepunkter små og eksplisitte
- Bruk allowlist for kommandoer
- Sanitise all loggoutput
- Ikke logg tokens, passord, private nøkler eller Cloudflare secrets

# Foreslått repo-struktur

```
hermes-ui/
  README.md
  docs/
    ARCHITECTURE.md
    API.md
    SECURITY.md
  backend/
    app.py
    commands.py
    config.py
    logs.py
  frontend/
  scripts/
  .planning/
```

# Cursor-prompt for oppstart

```
/gsd-new-project

Prosjekt: Hermes UI for Bob

Mål:
Lag et sikkert webbasert brukergrensesnitt for Hermes som kjører på Bob/Mac mini og eksponeres via Cloudflare Access.

Viktige begrensninger:
- Ikke bygg fri terminal i nettleseren.
- Bruk kun godkjente kommandoer via allowlist.
- Ikke eksponer secrets i logger eller UI.
- Start med minimal MVP: status, Hermes-status, restart og loggvisning.
- Følg GSD Master-flyt: discuss → plan → execute → verify.
```

# Cursor-prompt for kartlegging

```
/gsd-discuss-phase

Kartlegg eksisterende Hermes/Bob-oppsett før kode skrives.

Finn og dokumenter:
- Hvordan Hermes startes i dag
- Hvordan Hermes stoppes
- Hvordan Hermes restartes
- Hvor loggene ligger
- Om launchctl brukes
- Om Docker brukes
- Hvilken lokal port Hermes UI bør bruke
- Hvordan Cloudflare Tunnel bør peke mot tjenesten

Ikke endre filer i denne fasen med mindre det er dokumentasjonsfiler.
```

# Cursor-prompt for første implementering

```
/gsd-plan-phase

Lag en liten implementeringsplan for første MVP.

Planen skal kun inneholde:
1. Opprett repo-/filstruktur
2. Lag GET /api/status
3. Lag enkel dashboard-side som viser status

Ikke implementer start/stop/restart før status-endepunktet er verifisert.
```

# Git-kommandoer

```bash
git status
```

```bash
git add .
git commit -m "chore: initialize hermes ui project"
```

```bash
git add .
git commit -m "feat: add status endpoint"
```

```bash
git add .
git commit -m "docs: add architecture notes"
```