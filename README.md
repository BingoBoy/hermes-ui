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
