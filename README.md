# rezensionintegrator

Selbstgehostetes Google-Reviews-Widget für [fullflightsim.de](https://www.fullflightsim.de).

## Aufbau
- `fetcher/` — Python-Skripte, holen Reviews von Google und schreiben `docs/reviews.json`.
- `docs/` — Widget-Dateien (von GitHub Pages ausgeliefert).
- `.github/workflows/fetch.yml` — GitHub Action, täglich 03:00 UTC.

## Entwicklung
```bash
pip install -r fetcher/requirements.txt
pytest
```

## Design
Siehe [docs/superpowers/specs/2026-04-21-rezensionintegrator-design.md](docs/superpowers/specs/2026-04-21-rezensionintegrator-design.md).
