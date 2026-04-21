# rezensionintegrator

Selbstgehostetes Google-Reviews-Widget für [fullflightsim.de](https://www.fullflightsim.de) — Ablöse des Trustindex-Widgets.

## Architektur

```
Google Places API  ─► GitHub Action (täglich)  ─► docs/reviews.json
                                                 ─► docs/avatars/*.jpg
                                                          │
                                                          ▼
                                                 GitHub Pages (CDN)
                                                          │
                                                          ▼
                             Duda-Website: 3 Zeilen HTML  ─►  Widget
```

- `fetcher/` — Python-Skripte, holen Reviews von Google, normalisieren, cachen Avatare.
- `docs/` — Alles was GitHub Pages ausliefert: `widget.js`, `widget.css`, `reviews.json`, `avatars/*.jpg`.
- `.github/workflows/fetch.yml` — Daily Cron (03:00 UTC) + manueller Trigger.

## Setup (lokal)

```bash
pip install -r fetcher/requirements.txt
pytest                                  # alle Tests grün
```

Fetcher lokal testen (benötigt API-Key):

```bash
export PLACE_ID=ChIJZybyS393vUcRmrlk8nxVyuE
export GOOGLE_MAPS_API_KEY=<dein_key>
export REVIEWS_SOURCE=places
python -m fetcher.fetch
```

Widget lokal testen:

```bash
python -m http.server 8000 --directory docs
# → http://localhost:8000
```

## Phase 2 aktivieren (nach Google-Quota-Freigabe)

Die Business Profile API ist seit 2026-04-17 bei Google beantragt. Nach Freigabe:

1. `fetcher/business_api.py` implementieren (siehe Kommentar im File, Basis ist `RENZENSIONBEANTWORTER/reviews_fetcher.py`).
2. Secrets in GitHub setzen: `GOOGLE_OAUTH_CLIENT_ID`, `GOOGLE_OAUTH_CLIENT_SECRET`, `GOOGLE_OAUTH_REFRESH_TOKEN`.
3. In `.github/workflows/fetch.yml` `REVIEWS_SOURCE: business` setzen.
4. Workflow manuell triggern — alle ~217 Reviews erscheinen.

## Einbettung auf Duda

In der Duda-Seite einen `HTML`/`Embed Code`-Baustein einfügen:

```html
<div id="ffs-google-reviews"></div>
<link rel="stylesheet" href="https://firefly1502.github.io/rezensionintegrator/widget.css">
<script src="https://firefly1502.github.io/rezensionintegrator/widget.js" defer></script>
```

## Troubleshooting

- **Action rot, `403 PERMISSION_DENIED`:** API-Key ist auf Places API (New) beschränkt — prüfen, ob der Key noch gültig ist und das richtige Projekt aktiv hat.
- **Widget zeigt sich nicht:** Browser-Dev-Tools → Console → Error-Message. Das Widget versteckt sich bei Fehlern absichtlich.
- **Avatar-Datei 404:** Fetcher hat sie noch nicht geladen — Workflow manuell triggern.

## Dokumente

- Spec: [docs/superpowers/specs/2026-04-21-rezensionintegrator-design.md](docs/superpowers/specs/2026-04-21-rezensionintegrator-design.md)
- Plan: [docs/superpowers/plans/2026-04-21-rezensionintegrator-v1.md](docs/superpowers/plans/2026-04-21-rezensionintegrator-v1.md)
- Datenschutz-Entwürfe: [docs/datenschutz-text-entwuerfe.md](docs/datenschutz-text-entwuerfe.md)
