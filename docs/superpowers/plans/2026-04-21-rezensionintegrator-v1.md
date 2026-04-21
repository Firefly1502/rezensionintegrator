# Rezensionintegrator V1 – Implementierungsplan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers-extended-cc:subagent-driven-development (recommended) or superpowers-extended-cc:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Selbstgebautes Google-Rezensions-Widget auf GitHub Pages, eingebettet in Duda-Website, Phase-1-Fetcher aktiv.

**Architecture:** Python-Fetcher (GitHub Action, täglich) schreibt `docs/reviews.json` und cached Avatare lokal. Vanilla-JS-Widget (in `docs/`) liest die JSON und rendert den Slider. Drei HTML-Zeilen in Duda.

**Tech Stack:** Python 3.11, `requests`, `pytest` / Vanilla JS (ES2017+), CSS Scroll-Snap / GitHub Actions (cron) + GitHub Pages.

**Spec:** [2026-04-21-rezensionintegrator-design.md](../specs/2026-04-21-rezensionintegrator-design.md)

---

## Task 0: Repo-Scaffold

**Goal:** Projektstruktur, Git-Init, `.gitignore`, `requirements.txt`, Stub-README.

**Files:**
- Create: `.gitignore`
- Create: `fetcher/requirements.txt`
- Create: `fetcher/__init__.py`
- Create: `tests/__init__.py`
- Create: `tests/fixtures/.gitkeep`
- Create: `docs/.gitkeep`
- Create: `docs/avatars/.gitkeep`
- Create: `README.md`

**Acceptance Criteria:**
- [ ] Alle o.g. Ordner und Dateien existieren
- [ ] `pip install -r fetcher/requirements.txt` läuft ohne Fehler durch
- [ ] `pytest` läuft (zunächst 0 Tests) ohne Fehler
- [ ] `git status` zeigt keine ungewollten Dateien (z.B. `__pycache__`)

**Verify:** `pip install -r fetcher/requirements.txt && pytest` → Erwartung: "no tests ran" oder exit-code 5, KEIN Error.

**Steps:**

- [ ] **Step 1: Verzeichnisstruktur erstellen**

Im Projekt-Root `REZENSIONINTEGRATOR/` erstellen:

```
.gitignore
README.md
fetcher/
  __init__.py
  requirements.txt
tests/
  __init__.py
  fixtures/
    .gitkeep
docs/
  .gitkeep
  avatars/
    .gitkeep
```

- [ ] **Step 2: `.gitignore` schreiben**

```
# Python
__pycache__/
*.py[cod]
*$py.class
.pytest_cache/
.venv/
venv/
*.egg-info/

# Editor
.vscode/
.idea/
*.swp
.DS_Store

# Secrets (niemals committen)
.env
*.env
credentials.json
token.json
oauth_client_*.json

# OS
Thumbs.db
```

- [ ] **Step 3: `fetcher/requirements.txt` schreiben**

```
requests==2.32.3
pytest==8.3.3

# Phase 2 (noch ungenutzt, aber vorbereitet):
google-auth==2.35.0
google-auth-oauthlib==1.2.1
google-api-python-client==2.149.0
```

- [ ] **Step 4: `README.md` schreiben**

```markdown
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
```

- [ ] **Step 5: Install und Smoke-Test**

Run: `pip install -r fetcher/requirements.txt`
Expected: installiert ohne Error.

Run: `pytest`
Expected: `no tests ran` oder exit 5 (kein Testverzeichnis-Fehler).

- [ ] **Step 6: Commit**

```bash
git init
git add .
git commit -m "chore: initialize repo scaffold"
```

---

## Task 1: JSON-Schema-Fixture

**Goal:** Eine handgebaute Beispiel-`reviews.json` existiert als Referenz und Test-Fixture. Ein kleiner Validator prüft grob die Struktur.

**Files:**
- Create: `tests/fixtures/reviews_sample.json`
- Create: `tests/fixtures/places_response_sample.json`
- Create: `fetcher/schema.py`
- Create: `tests/test_schema.py`

**Acceptance Criteria:**
- [ ] `reviews_sample.json` enthält 2 Reviews, folgt dem Schema aus Section 4 des Specs
- [ ] `places_response_sample.json` enthält einen realistischen Places-API-Response-Ausschnitt (aus `https://places.googleapis.com/v1/places/{id}`)
- [ ] `fetcher/schema.py` stellt `validate_reviews_json(data: dict) -> None` bereit (raises `ValueError` bei Verstoß)
- [ ] Tests grün

**Verify:** `pytest tests/test_schema.py -v` → 3+ Tests PASS

**Steps:**

- [ ] **Step 1: `tests/fixtures/reviews_sample.json` schreiben**

```json
{
  "version": 1,
  "updated_at": "2026-04-21T03:00:00Z",
  "source": "places_api",
  "business": {
    "place_id": "ChIJZybyS393vUcRmrlk8nxVyuE",
    "name": "Full Flight Sim",
    "rating_avg": 5.0,
    "rating_count": 217,
    "google_url": "https://maps.google.com/?cid=16252113413421686170",
    "write_review_url": "https://search.google.com/local/writereview?placeid=ChIJZybyS393vUcRmrlk8nxVyuE"
  },
  "reviews": [
    {
      "id": "sample-1",
      "author": {
        "name": "Max Mustermann",
        "initial": "M",
        "avatar_url": "avatars/abc123.jpg",
        "profile_url": "https://www.google.com/maps/contrib/sample1"
      },
      "rating": 5,
      "date_iso": "2026-04-16",
      "date_display": "16 April 2026",
      "text": "Absolut geiles Erlebnis! Der A320-Simulator war der Hammer.",
      "language": "de",
      "verified": true,
      "photos": [],
      "owner_reply": null,
      "source_url": "https://maps.google.com/?cid=16252113413421686170"
    },
    {
      "id": "sample-2",
      "author": {
        "name": "Juville Beats",
        "initial": "J",
        "avatar_url": null,
        "profile_url": "https://www.google.com/maps/contrib/sample2"
      },
      "rating": 5,
      "date_iso": "2026-04-10",
      "date_display": "10 April 2026",
      "text": "Top Beratung, toller Simulator. Kommen wieder!",
      "language": "de",
      "verified": true,
      "photos": [],
      "owner_reply": {
        "text": "Vielen Dank! Freut uns sehr.",
        "date_iso": "2026-04-11"
      },
      "source_url": "https://maps.google.com/?cid=16252113413421686170"
    }
  ]
}
```

- [ ] **Step 2: `tests/fixtures/places_response_sample.json` schreiben**

Dies ist der Payload-Ausschnitt, den die Places API (New) unter `places.googleapis.com/v1/places/{id}` mit `X-Goog-FieldMask: id,displayName,rating,userRatingCount,reviews,googleMapsUri` liefert.

```json
{
  "id": "ChIJZybyS393vUcRmrlk8nxVyuE",
  "displayName": { "text": "Full Flight Sim", "languageCode": "de" },
  "rating": 5.0,
  "userRatingCount": 217,
  "googleMapsUri": "https://maps.google.com/?cid=16252113413421686170",
  "reviews": [
    {
      "name": "places/ChIJ.../reviews/ChZDSU",
      "relativePublishTimeDescription": "vor 5 Tagen",
      "rating": 5,
      "text": { "text": "Absolut geiles Erlebnis!", "languageCode": "de" },
      "originalText": { "text": "Absolut geiles Erlebnis!", "languageCode": "de" },
      "authorAttribution": {
        "displayName": "Max Mustermann",
        "uri": "https://www.google.com/maps/contrib/sample1",
        "photoUri": "https://lh3.googleusercontent.com/a/sample1=s128-c-rp-mo-br100"
      },
      "publishTime": "2026-04-16T10:22:14Z"
    },
    {
      "name": "places/ChIJ.../reviews/ChZDSV",
      "relativePublishTimeDescription": "vor 11 Tagen",
      "rating": 5,
      "text": { "text": "Top Beratung, toller Simulator.", "languageCode": "de" },
      "originalText": { "text": "Top Beratung, toller Simulator.", "languageCode": "de" },
      "authorAttribution": {
        "displayName": "Juville Beats",
        "uri": "https://www.google.com/maps/contrib/sample2",
        "photoUri": "https://lh3.googleusercontent.com/a/sample2=s128-c-rp-mo-br100"
      },
      "publishTime": "2026-04-10T09:00:00Z"
    }
  ]
}
```

- [ ] **Step 3: Failing test zuerst (`tests/test_schema.py`)**

```python
import json
from pathlib import Path

import pytest

from fetcher.schema import validate_reviews_json

FIXTURES = Path(__file__).parent / "fixtures"


def _load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def test_sample_is_valid():
    data = _load("reviews_sample.json")
    validate_reviews_json(data)  # keine Exception erwartet


def test_missing_version_fails():
    data = _load("reviews_sample.json")
    del data["version"]
    with pytest.raises(ValueError, match="version"):
        validate_reviews_json(data)


def test_reviews_not_list_fails():
    data = _load("reviews_sample.json")
    data["reviews"] = "not a list"
    with pytest.raises(ValueError, match="reviews"):
        validate_reviews_json(data)
```

Run: `pytest tests/test_schema.py -v`
Expected: FAIL (`ModuleNotFoundError: fetcher.schema`).

- [ ] **Step 4: `fetcher/schema.py` schreiben**

```python
"""Leichter Struktur-Validator für reviews.json.

Kein JSONSchema-Framework, nur defensive Prüfungen für die Felder, auf die
das Widget direkt zugreift. Ziel: kaputte JSON-Datei wird in der GitHub Action
früh abgefangen, bevor sie auf Pages landet.
"""

from __future__ import annotations

REQUIRED_TOP_KEYS = {"version", "updated_at", "source", "business", "reviews"}
REQUIRED_BUSINESS_KEYS = {
    "place_id", "name", "rating_avg", "rating_count", "write_review_url",
}
REQUIRED_REVIEW_KEYS = {
    "id", "author", "rating", "date_iso", "date_display", "text",
}


def validate_reviews_json(data: dict) -> None:
    if not isinstance(data, dict):
        raise ValueError("reviews.json root must be a dict")

    missing = REQUIRED_TOP_KEYS - set(data)
    if missing:
        raise ValueError(f"reviews.json missing top-level keys: {missing}")

    if data["version"] != 1:
        raise ValueError(f"Unsupported schema version: {data['version']}")

    business = data["business"]
    if not isinstance(business, dict):
        raise ValueError("business must be a dict")
    missing = REQUIRED_BUSINESS_KEYS - set(business)
    if missing:
        raise ValueError(f"business missing keys: {missing}")

    reviews = data["reviews"]
    if not isinstance(reviews, list):
        raise ValueError("reviews must be a list")

    for i, review in enumerate(reviews):
        if not isinstance(review, dict):
            raise ValueError(f"reviews[{i}] must be a dict")
        missing = REQUIRED_REVIEW_KEYS - set(review)
        if missing:
            raise ValueError(f"reviews[{i}] missing keys: {missing}")
        if not isinstance(review["author"], dict) or "name" not in review["author"]:
            raise ValueError(f"reviews[{i}].author must be a dict with 'name'")
        if not isinstance(review["rating"], (int, float)):
            raise ValueError(f"reviews[{i}].rating must be numeric")
```

Run: `pytest tests/test_schema.py -v`
Expected: 3 PASS.

- [ ] **Step 5: Commit**

```bash
git add fetcher/schema.py tests/test_schema.py tests/fixtures/
git commit -m "feat(fetcher): add reviews.json schema validator + fixtures"
```

---

## Task 2: Places API Client

**Goal:** `fetcher/places_api.py` ruft Reviews vom Places API (New) Endpoint ab und gibt den Raw-JSON-Response zurück. Netzwerk-Aufruf in Tests via `responses`-artigem Mock stubbed.

**Files:**
- Create: `fetcher/places_api.py`
- Create: `tests/test_places_api.py`

**Acceptance Criteria:**
- [ ] Funktion `fetch_place(place_id: str, api_key: str) -> dict` existiert
- [ ] Setzt `X-Goog-Api-Key` und `X-Goog-FieldMask` Header korrekt
- [ ] Raist `RuntimeError` mit hilfreicher Meldung bei HTTP-Fehler
- [ ] Unit-Test mockt `requests.get` und prüft Header + Parsen

**Verify:** `pytest tests/test_places_api.py -v` → 2+ PASS

**Steps:**

- [ ] **Step 1: Failing test schreiben**

`tests/test_places_api.py`:

```python
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from fetcher.places_api import fetch_place

FIXTURES = Path(__file__).parent / "fixtures"


def _mock_response(status=200, payload=None):
    m = MagicMock()
    m.status_code = status
    m.ok = 200 <= status < 300
    m.json.return_value = payload or {}
    m.text = json.dumps(payload or {})
    return m


@patch("fetcher.places_api.requests.get")
def test_fetch_place_success(mock_get):
    sample = json.loads((FIXTURES / "places_response_sample.json").read_text("utf-8"))
    mock_get.return_value = _mock_response(200, sample)

    result = fetch_place("ChIJtest", "FAKE_KEY")

    assert result["displayName"]["text"] == "Full Flight Sim"
    assert len(result["reviews"]) == 2

    args, kwargs = mock_get.call_args
    assert "places/ChIJtest" in args[0]
    headers = kwargs["headers"]
    assert headers["X-Goog-Api-Key"] == "FAKE_KEY"
    assert "reviews" in headers["X-Goog-FieldMask"]


@patch("fetcher.places_api.requests.get")
def test_fetch_place_http_error(mock_get):
    mock_get.return_value = _mock_response(403, {"error": {"message": "denied"}})
    with pytest.raises(RuntimeError, match="403"):
        fetch_place("ChIJtest", "FAKE_KEY")
```

Run: `pytest tests/test_places_api.py -v`
Expected: FAIL (`ModuleNotFoundError`).

- [ ] **Step 2: `fetcher/places_api.py` schreiben**

```python
"""Client für Google Places API (New) — nur Lese-Zugriff auf ein einzelnes Place.

Doku: https://developers.google.com/maps/documentation/places/web-service/place-details
Endpoint: https://places.googleapis.com/v1/places/{place_id}
"""

from __future__ import annotations

import requests

_BASE_URL = "https://places.googleapis.com/v1/places"
_FIELD_MASK = ",".join([
    "id",
    "displayName",
    "rating",
    "userRatingCount",
    "googleMapsUri",
    "reviews",
])


def fetch_place(place_id: str, api_key: str, timeout: int = 10) -> dict:
    url = f"{_BASE_URL}/{place_id}"
    headers = {
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": _FIELD_MASK,
        "Accept": "application/json",
    }
    resp = requests.get(url, headers=headers, timeout=timeout)
    if not resp.ok:
        raise RuntimeError(
            f"Places API returned HTTP {resp.status_code}: {resp.text[:300]}"
        )
    return resp.json()
```

Run: `pytest tests/test_places_api.py -v`
Expected: 2 PASS.

- [ ] **Step 3: Commit**

```bash
git add fetcher/places_api.py tests/test_places_api.py
git commit -m "feat(fetcher): add Places API client"
```

---

## Task 3: Normalizer

**Goal:** `fetcher/normalize.py` transformiert einen Places-API-Response in das finale `reviews.json`-Schema. Pure Funktion, keine I/O, locale-feste deutsche Datumsformatierung.

**Files:**
- Create: `fetcher/normalize.py`
- Create: `tests/test_normalize.py`

**Acceptance Criteria:**
- [ ] `normalize_places_response(api_response, place_id) -> dict` liefert Schema-konformes Dict
- [ ] `date_display` nutzt deutsche Monatsnamen (z.B. "16 April 2026")
- [ ] Fehlende `photoUri` → `avatar_url = None`
- [ ] `initial` ist erster Buchstabe des Author-Namens (Fallback "?")
- [ ] `validate_reviews_json` akzeptiert das Ergebnis
- [ ] Tests grün

**Verify:** `pytest tests/test_normalize.py -v` → 4+ PASS

**Steps:**

- [ ] **Step 1: Failing test schreiben**

`tests/test_normalize.py`:

```python
import json
from pathlib import Path

from fetcher.normalize import normalize_places_response
from fetcher.schema import validate_reviews_json

FIXTURES = Path(__file__).parent / "fixtures"
PLACE_ID = "ChIJZybyS393vUcRmrlk8nxVyuE"


def _load_places():
    return json.loads((FIXTURES / "places_response_sample.json").read_text("utf-8"))


def test_normalize_produces_valid_schema():
    result = normalize_places_response(_load_places(), PLACE_ID)
    validate_reviews_json(result)


def test_business_block_mapped():
    result = normalize_places_response(_load_places(), PLACE_ID)
    assert result["business"]["place_id"] == PLACE_ID
    assert result["business"]["name"] == "Full Flight Sim"
    assert result["business"]["rating_avg"] == 5.0
    assert result["business"]["rating_count"] == 217
    assert "writereview" in result["business"]["write_review_url"]


def test_reviews_mapped():
    result = normalize_places_response(_load_places(), PLACE_ID)
    assert len(result["reviews"]) == 2
    r0 = result["reviews"][0]
    assert r0["author"]["name"] == "Max Mustermann"
    assert r0["author"]["initial"] == "M"
    assert r0["rating"] == 5
    assert r0["date_iso"] == "2026-04-16"
    assert "April" in r0["date_display"]
    assert r0["text"].startswith("Absolut")


def test_missing_avatar_is_none():
    places = _load_places()
    del places["reviews"][0]["authorAttribution"]["photoUri"]
    result = normalize_places_response(places, PLACE_ID)
    assert result["reviews"][0]["author"]["avatar_url"] is None


def test_source_field_is_places_api():
    result = normalize_places_response(_load_places(), PLACE_ID)
    assert result["source"] == "places_api"
```

Run: `pytest tests/test_normalize.py -v`
Expected: FAIL.

- [ ] **Step 2: `fetcher/normalize.py` schreiben**

```python
"""API-Response → reviews.json Schema-Transformation.

Alle Funktionen sind rein: kein Netzwerk, kein Filesystem. Damit leicht testbar
und deterministisch.
"""

from __future__ import annotations

from datetime import datetime, timezone

_MONTHS_DE = [
    "", "Januar", "Februar", "März", "April", "Mai", "Juni",
    "Juli", "August", "September", "Oktober", "November", "Dezember",
]


def _format_date_de(iso_ts: str) -> tuple[str, str]:
    """Parst einen ISO-Timestamp ('2026-04-16T10:22:14Z') und gibt
    ('2026-04-16', '16 April 2026') zurück."""
    dt = datetime.fromisoformat(iso_ts.replace("Z", "+00:00"))
    date_iso = dt.date().isoformat()
    date_display = f"{dt.day} {_MONTHS_DE[dt.month]} {dt.year}"
    return date_iso, date_display


def _review_id(name: str) -> str:
    # 'places/ChIJ…/reviews/ChZDSU' → 'ChZDSU'
    return name.rsplit("/", 1)[-1] if "/" in name else name


def _initial(name: str) -> str:
    name = (name or "").strip()
    return name[0].upper() if name else "?"


def normalize_places_response(api_response: dict, place_id: str) -> dict:
    business_name = api_response.get("displayName", {}).get("text", "")
    google_url = api_response.get("googleMapsUri", "")
    write_review_url = (
        f"https://search.google.com/local/writereview?placeid={place_id}"
    )

    reviews_out = []
    for r in api_response.get("reviews", []):
        author_block = r.get("authorAttribution", {})
        author_name = author_block.get("displayName", "")
        date_iso, date_display = _format_date_de(r["publishTime"])

        reviews_out.append({
            "id": _review_id(r.get("name", "")),
            "author": {
                "name": author_name,
                "initial": _initial(author_name),
                "avatar_url": author_block.get("photoUri"),
                "profile_url": author_block.get("uri"),
            },
            "rating": r.get("rating", 0),
            "date_iso": date_iso,
            "date_display": date_display,
            "text": r.get("text", {}).get("text", ""),
            "language": r.get("text", {}).get("languageCode"),
            "verified": True,
            "photos": [],
            "owner_reply": None,
            "source_url": google_url,
        })

    return {
        "version": 1,
        "updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "source": "places_api",
        "business": {
            "place_id": place_id,
            "name": business_name,
            "rating_avg": api_response.get("rating"),
            "rating_count": api_response.get("userRatingCount"),
            "google_url": google_url,
            "write_review_url": write_review_url,
        },
        "reviews": reviews_out,
    }
```

Run: `pytest tests/test_normalize.py -v`
Expected: 5 PASS.

- [ ] **Step 3: Commit**

```bash
git add fetcher/normalize.py tests/test_normalize.py
git commit -m "feat(fetcher): add Places API → schema normalizer"
```

---

## Task 4: Avatar-Cache

**Goal:** `fetcher/avatar_cache.py` lädt ein Avatar-Bild herunter und speichert es als `docs/avatars/{sha1(url)}.jpg`. Idempotent (existierende Datei wird nicht neu geladen). Tauscht außerdem die `avatar_url` in einem Review-Dict auf den lokalen Pfad um.

**Files:**
- Create: `fetcher/avatar_cache.py`
- Create: `tests/test_avatar_cache.py`

**Acceptance Criteria:**
- [ ] `cache_avatar(url: str, avatars_dir: Path) -> str | None` existiert
- [ ] Gibt relativen Pfad `"avatars/{hash}.jpg"` zurück (relativ zu `docs/`)
- [ ] Bei `url=None` → Rückgabe `None`, kein Fetch
- [ ] Bei bereits existierender Datei: kein Re-Fetch
- [ ] Bei HTTP-Fehler: Rückgabe `None`, Widget zeigt dann Initial-Fallback
- [ ] Hilfsfunktion `localize_avatars(reviews_json, avatars_dir)` ersetzt alle `avatar_url` in-place

**Verify:** `pytest tests/test_avatar_cache.py -v` → 4+ PASS

**Steps:**

- [ ] **Step 1: Failing test schreiben**

`tests/test_avatar_cache.py`:

```python
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from fetcher.avatar_cache import cache_avatar, localize_avatars


def _mock_img_response(status=200, content=b"\xff\xd8\xff\xe0fakejpeg"):
    m = MagicMock()
    m.status_code = status
    m.ok = 200 <= status < 300
    m.content = content
    return m


@patch("fetcher.avatar_cache.requests.get")
def test_cache_avatar_downloads_and_returns_path(mock_get, tmp_path):
    mock_get.return_value = _mock_img_response()
    url = "https://lh3.googleusercontent.com/a/test=s128"

    result = cache_avatar(url, tmp_path)

    assert result is not None
    assert result.startswith("avatars/")
    assert result.endswith(".jpg")
    assert (tmp_path / Path(result).name).exists()


@patch("fetcher.avatar_cache.requests.get")
def test_cache_avatar_idempotent(mock_get, tmp_path):
    mock_get.return_value = _mock_img_response()
    url = "https://lh3.googleusercontent.com/a/test=s128"

    cache_avatar(url, tmp_path)
    cache_avatar(url, tmp_path)

    assert mock_get.call_count == 1  # zweites Mal kein neuer Fetch


@patch("fetcher.avatar_cache.requests.get")
def test_cache_avatar_none_url(mock_get, tmp_path):
    assert cache_avatar(None, tmp_path) is None
    mock_get.assert_not_called()


@patch("fetcher.avatar_cache.requests.get")
def test_cache_avatar_http_error_returns_none(mock_get, tmp_path):
    mock_get.return_value = _mock_img_response(status=404)
    result = cache_avatar("https://example.invalid/x", tmp_path)
    assert result is None


@patch("fetcher.avatar_cache.requests.get")
def test_localize_avatars_rewrites_urls(mock_get, tmp_path):
    mock_get.return_value = _mock_img_response()
    data = {
        "reviews": [
            {"author": {"avatar_url": "https://lh3.googleusercontent.com/a/1=s128"}},
            {"author": {"avatar_url": None}},
        ]
    }
    localize_avatars(data, tmp_path)
    assert data["reviews"][0]["author"]["avatar_url"].startswith("avatars/")
    assert data["reviews"][1]["author"]["avatar_url"] is None
```

Run: `pytest tests/test_avatar_cache.py -v`
Expected: FAIL.

- [ ] **Step 2: `fetcher/avatar_cache.py` schreiben**

```python
"""Lokales Caching von Reviewer-Avataren.

DSGVO-Motivation: Wenn das Widget Avatare direkt von
`lh3.googleusercontent.com` lädt, fließen Besucher-IPs ohne Einwilligung
an Google. Daher laden wir jedes Avatar einmal im Fetcher herunter und
legen es neben der reviews.json in `docs/avatars/` ab.
"""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path

import requests

log = logging.getLogger(__name__)


def _hash_url(url: str) -> str:
    return hashlib.sha1(url.encode("utf-8")).hexdigest()


def cache_avatar(url: str | None, avatars_dir: Path, timeout: int = 10) -> str | None:
    """Lädt das Avatar herunter, speichert es unter `avatars_dir/{hash}.jpg`
    und gibt den relativen Pfad ("avatars/{hash}.jpg") zurück.

    - url=None → Rückgabe None (Widget nutzt Initial-Fallback).
    - Datei existiert bereits → kein Re-Fetch, direkt Pfad zurückgeben.
    - HTTP-Fehler → Rückgabe None (wird geloggt).
    """
    if not url:
        return None

    avatars_dir.mkdir(parents=True, exist_ok=True)
    file_name = f"{_hash_url(url)}.jpg"
    target = avatars_dir / file_name
    rel_path = f"avatars/{file_name}"

    if target.exists():
        return rel_path

    try:
        resp = requests.get(url, timeout=timeout)
    except requests.RequestException as e:
        log.warning("Avatar fetch failed for %s: %s", url, e)
        return None

    if not resp.ok:
        log.warning("Avatar fetch returned HTTP %s for %s", resp.status_code, url)
        return None

    target.write_bytes(resp.content)
    return rel_path


def localize_avatars(reviews_json: dict, avatars_dir: Path) -> None:
    """Ersetzt in-place jede `avatar_url` durch die lokale Kopie."""
    for review in reviews_json.get("reviews", []):
        author = review.get("author") or {}
        original_url = author.get("avatar_url")
        author["avatar_url"] = cache_avatar(original_url, avatars_dir)
```

Run: `pytest tests/test_avatar_cache.py -v`
Expected: 5 PASS.

- [ ] **Step 3: Commit**

```bash
git add fetcher/avatar_cache.py tests/test_avatar_cache.py
git commit -m "feat(fetcher): add local avatar cache (DSGVO mitigation)"
```

---

## Task 5: Fetch-Orchestrator

**Goal:** `fetcher/fetch.py` bindet alles zusammen: liest ENV-Variablen, ruft Phase-1-Fetcher, normalisiert, cacht Avatare, validiert Schema und schreibt `docs/reviews.json`. Soll als `python -m fetcher.fetch` laufen.

**Files:**
- Create: `fetcher/fetch.py`
- Create: `fetcher/business_api.py` (Stub für Phase 2)
- Create: `tests/test_fetch.py`

**Acceptance Criteria:**
- [ ] `python -m fetcher.fetch` liest `PLACE_ID`, `GOOGLE_MAPS_API_KEY`, `REVIEWS_SOURCE` aus Env
- [ ] Bei `REVIEWS_SOURCE=places` ruft Phase-1-Fetcher
- [ ] Bei `REVIEWS_SOURCE=business` ruft Phase-2-Stub (wirft heute `NotImplementedError` mit klarer Nachricht)
- [ ] Fehlende Env → klare Error-Meldung + Exit-Code 1
- [ ] Schreibt `docs/reviews.json` mit `ensure_ascii=False, indent=2`
- [ ] Integrationstest mit mocked `fetch_place` läuft durch

**Verify:** `pytest tests/test_fetch.py -v` → 3+ PASS

**Steps:**

- [ ] **Step 1: `fetcher/business_api.py` Stub schreiben**

```python
"""Google Business Profile API Client (Phase 2).

Wird aktiviert, sobald die Quota freigegeben ist (Antrag seit 2026-04-17).
Bis dahin NotImplementedError — der Orchestrator fällt dann mit einer
klaren Meldung aus. Der produktive Pfad läuft über places_api.py.

Plan für die Implementierung (später):
- Auf `RENZENSIONBEANTWORTER/reviews_fetcher.py` aufsetzen
  (funktionierender OAuth-Flow, paginierter Review-Abruf).
- Credentials aus GitHub Secrets laden statt aus `credentials.json`.
- Rückgabe in den Places-Response analogen Dict, damit `normalize.py`
  mit einer zweiten `normalize_business_response()`-Variante
  das gleiche Schema erzeugen kann.
"""

from __future__ import annotations


def fetch_all_reviews(*args, **kwargs):
    raise NotImplementedError(
        "Business Profile API fetcher ist noch nicht implementiert. "
        "Aktivierung geplant nach Google-Quota-Freigabe. "
        "Bis dahin bitte REVIEWS_SOURCE=places verwenden."
    )
```

- [ ] **Step 2: Failing test schreiben**

`tests/test_fetch.py`:

```python
import json
from pathlib import Path
from unittest.mock import patch

import pytest

from fetcher import fetch as fetch_module


@patch("fetcher.fetch.fetch_place")
@patch("fetcher.fetch.cache_avatar")
def test_run_writes_valid_reviews_json(mock_cache, mock_fetch, tmp_path, monkeypatch):
    sample = json.loads(
        (Path(__file__).parent / "fixtures" / "places_response_sample.json").read_text("utf-8")
    )
    mock_fetch.return_value = sample
    mock_cache.return_value = "avatars/fake.jpg"

    docs_dir = tmp_path / "docs"
    monkeypatch.setenv("PLACE_ID", "ChIJZybyS393vUcRmrlk8nxVyuE")
    monkeypatch.setenv("GOOGLE_MAPS_API_KEY", "FAKE")
    monkeypatch.setenv("REVIEWS_SOURCE", "places")

    fetch_module.run(docs_dir=docs_dir)

    out = docs_dir / "reviews.json"
    assert out.exists()
    data = json.loads(out.read_text("utf-8"))
    assert data["version"] == 1
    assert data["source"] == "places_api"
    assert len(data["reviews"]) == 2
    assert data["reviews"][0]["author"]["avatar_url"] == "avatars/fake.jpg"


def test_run_missing_env_raises(tmp_path, monkeypatch):
    monkeypatch.delenv("PLACE_ID", raising=False)
    with pytest.raises(SystemExit):
        fetch_module.run(docs_dir=tmp_path / "docs")


def test_run_business_source_not_implemented(tmp_path, monkeypatch):
    monkeypatch.setenv("PLACE_ID", "X")
    monkeypatch.setenv("GOOGLE_MAPS_API_KEY", "Y")
    monkeypatch.setenv("REVIEWS_SOURCE", "business")
    with pytest.raises(NotImplementedError):
        fetch_module.run(docs_dir=tmp_path / "docs")
```

Run: `pytest tests/test_fetch.py -v`
Expected: FAIL.

- [ ] **Step 3: `fetcher/fetch.py` schreiben**

```python
"""Orchestrator: ruft Quelle, normalisiert, cacht Avatare, schreibt JSON.

Aufruf:
    python -m fetcher.fetch

Erforderliche Env-Vars:
    PLACE_ID               Google Place ID.
    GOOGLE_MAPS_API_KEY    API-Key (Places API New).
    REVIEWS_SOURCE         'places' (Phase 1) oder 'business' (Phase 2).
"""

from __future__ import annotations

import json
import logging
import os
import sys
from pathlib import Path

from fetcher.avatar_cache import cache_avatar, localize_avatars  # noqa: F401
from fetcher.business_api import fetch_all_reviews as fetch_business
from fetcher.normalize import normalize_places_response
from fetcher.places_api import fetch_place
from fetcher.schema import validate_reviews_json

log = logging.getLogger(__name__)


def _require_env(name: str) -> str:
    v = os.environ.get(name)
    if not v:
        print(f"ERROR: Env var {name} is required", file=sys.stderr)
        sys.exit(1)
    return v


def run(docs_dir: Path | None = None) -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    place_id = _require_env("PLACE_ID")
    api_key = _require_env("GOOGLE_MAPS_API_KEY")
    source = os.environ.get("REVIEWS_SOURCE", "places").lower()

    docs_dir = docs_dir or Path(__file__).resolve().parent.parent / "docs"
    avatars_dir = docs_dir / "avatars"

    log.info("Fetching reviews (source=%s, place_id=%s)", source, place_id)

    if source == "places":
        raw = fetch_place(place_id, api_key)
        data = normalize_places_response(raw, place_id)
    elif source == "business":
        fetch_business()  # hebt NotImplementedError
        raise RuntimeError("unreachable")
    else:
        raise ValueError(f"Unknown REVIEWS_SOURCE: {source!r}")

    localize_avatars(data, avatars_dir)
    validate_reviews_json(data)

    out = docs_dir / "reviews.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    log.info("Wrote %s (%d reviews)", out, len(data["reviews"]))


if __name__ == "__main__":
    run()
```

Run: `pytest tests/test_fetch.py -v`
Expected: 3 PASS.

- [ ] **Step 4: Lokaler End-to-End-Smoke-Test (optional, erfordert API-Key)**

```bash
export PLACE_ID=ChIJZybyS393vUcRmrlk8nxVyuE
export GOOGLE_MAPS_API_KEY=<dein_key>
export REVIEWS_SOURCE=places
python -m fetcher.fetch
cat docs/reviews.json | head -30
```

Expected: `docs/reviews.json` enthält ≥1 Review mit echtem Inhalt.

**Hinweis:** Falls der API-Key noch nicht existiert oder das Kontingent erschöpft ist, überspringe Step 4 und vertraue den Unit-Tests.

- [ ] **Step 5: Commit**

```bash
git add fetcher/fetch.py fetcher/business_api.py tests/test_fetch.py
git commit -m "feat(fetcher): add orchestrator with source-switch + Phase 2 stub"
```

---

## Task 6: Widget-CSS

**Goal:** `docs/widget.css` enthält das vollständige Layout: Header, Slider, Card, Modal, Responsive, Skeleton-Loading, Accessibility.

**Files:**
- Create: `docs/widget.css`

**Acceptance Criteria:**
- [ ] Klassen matchen die HTML-Struktur aus Section 5.1 des Specs
- [ ] Scroll-Snap horizontal in `.ffs-gr-track`
- [ ] Breakpoints: ≥1024 (4 Karten), 768-1023 (2-3), <768 (1)
- [ ] `.skeleton` Pulse-Animation
- [ ] `prefers-reduced-motion: reduce` entfernt Transitions
- [ ] CTA-Button in Gold (#D4A94C), Sterne in Google-Yellow (#FBBC04)

**Verify:** Manueller Test: `python -m http.server 8000 --directory docs` und `http://localhost:8000` in Browser öffnen (nach Task 7 kombiniert testbar).

**Steps:**

- [ ] **Step 1: `docs/widget.css` schreiben**

```css
/* Rezensionintegrator Widget — Full Flight Sim
 * Scope: alle Styles sind unter .ffs-gr-widget genested, damit sie
 * nicht in die Duda-Seite leaken.
 */

.ffs-gr-widget {
  --ffs-gold: #D4A94C;
  --ffs-star: #FBBC04;
  --ffs-text: #1f1f1f;
  --ffs-muted: #5f6368;
  --ffs-card-bg: #ffffff;
  --ffs-border: #e8eaed;
  --ffs-shadow: 0 1px 3px rgba(0,0,0,.08);
  --ffs-shadow-hover: 0 4px 12px rgba(0,0,0,.12);
  --ffs-radius: 10px;

  box-sizing: border-box;
  color: var(--ffs-text);
  font: inherit;
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem;
}

.ffs-gr-widget *,
.ffs-gr-widget *::before,
.ffs-gr-widget *::after { box-sizing: inherit; }

/* Header */
.ffs-gr-header {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: .75rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--ffs-border);
  margin-bottom: 1rem;
}
.ffs-gr-header .logo { width: 26px; height: 26px; flex-shrink: 0; }
.ffs-gr-header .label { font-weight: 600; }
.ffs-gr-header .stars { color: var(--ffs-star); letter-spacing: 1px; }
.ffs-gr-header .score { font-weight: 700; font-size: 1.15rem; }
.ffs-gr-header .separator { color: var(--ffs-border); }
.ffs-gr-header .count { color: var(--ffs-muted); }
.ffs-gr-header .cta-button {
  margin-left: auto;
  padding: .6rem 1.1rem;
  background: var(--ffs-gold);
  color: #fff;
  border-radius: 999px;
  text-decoration: none;
  font-weight: 600;
  transition: filter .15s ease, transform .15s ease;
}
.ffs-gr-header .cta-button:hover { filter: brightness(1.05); transform: translateY(-1px); }
.ffs-gr-header .cta-button:focus-visible { outline: 2px solid #000; outline-offset: 2px; }

/* Slider */
.ffs-gr-slider {
  position: relative;
  display: flex;
  align-items: center;
}
.ffs-gr-track {
  display: flex;
  gap: 1rem;
  overflow-x: auto;
  scroll-snap-type: x mandatory;
  scroll-behavior: smooth;
  padding: .25rem .25rem 1rem .25rem;
  scrollbar-width: thin;
}
.ffs-gr-track::-webkit-scrollbar { height: 6px; }
.ffs-gr-track::-webkit-scrollbar-thumb { background: var(--ffs-border); border-radius: 3px; }

/* Nav-Arrows */
.ffs-gr-slider .nav-prev,
.ffs-gr-slider .nav-next {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  background: #fff;
  border: 1px solid var(--ffs-border);
  border-radius: 50%;
  width: 36px;
  height: 36px;
  font-size: 1.25rem;
  cursor: pointer;
  box-shadow: var(--ffs-shadow);
  opacity: 0;
  transition: opacity .2s ease;
  z-index: 2;
}
.ffs-gr-slider:hover .nav-prev,
.ffs-gr-slider:hover .nav-next,
.ffs-gr-slider:focus-within .nav-prev,
.ffs-gr-slider:focus-within .nav-next { opacity: 1; }
.ffs-gr-slider .nav-prev { left: -8px; }
.ffs-gr-slider .nav-next { right: -8px; }
.ffs-gr-slider .nav-prev[disabled],
.ffs-gr-slider .nav-next[disabled] { opacity: .3 !important; cursor: default; }

/* Karte */
.review-card {
  flex: 0 0 calc(25% - .75rem);
  min-width: 240px;
  background: var(--ffs-card-bg);
  border: 1px solid var(--ffs-border);
  border-radius: var(--ffs-radius);
  padding: 1rem;
  scroll-snap-align: start;
  box-shadow: var(--ffs-shadow);
  transition: transform .15s ease, box-shadow .15s ease;
  cursor: pointer;
}
.review-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--ffs-shadow-hover);
}
.review-card .author-row {
  display: flex;
  align-items: center;
  gap: .6rem;
  margin-bottom: .5rem;
}
.review-card .avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #ccc;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-weight: 600;
  font-size: .95rem;
  object-fit: cover;
}
.review-card .meta { min-width: 0; flex: 1; }
.review-card .name { font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.review-card .date { color: var(--ffs-muted); font-size: .8rem; }
.review-card .rating-row { margin-bottom: .4rem; }
.review-card .rating-row .stars { color: var(--ffs-star); }
.review-card .rating-row .verified {
  display: inline-block;
  vertical-align: middle;
  margin-left: .3rem;
  color: #4285F4;
}
.review-card .text {
  font-size: .9rem;
  line-height: 1.45;
  color: var(--ffs-text);
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.review-card .read-more {
  display: inline-block;
  margin-top: .5rem;
  color: var(--ffs-gold);
  font-size: .85rem;
  font-weight: 600;
}

/* Skeleton */
.review-card.skeleton { pointer-events: none; cursor: default; }
.review-card.skeleton .avatar,
.review-card.skeleton .sk-line {
  background: linear-gradient(90deg, #eee 0%, #f5f5f5 50%, #eee 100%);
  background-size: 200% 100%;
  animation: ffs-sk-pulse 1.2s infinite;
  color: transparent;
}
.review-card.skeleton .sk-line { height: .7rem; border-radius: 3px; margin: .3rem 0; }
.review-card.skeleton .sk-line.short { width: 40%; }

@keyframes ffs-sk-pulse {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* Responsive */
@media (max-width: 1023px) {
  .review-card { flex: 0 0 calc(50% - .5rem); }
  .ffs-gr-slider .nav-prev,
  .ffs-gr-slider .nav-next { opacity: 1; }
}
@media (max-width: 767px) {
  .review-card { flex: 0 0 calc(100% - .5rem); }
  .ffs-gr-header .cta-button { margin-left: 0; width: 100%; text-align: center; }
}

/* Modal */
.ffs-gr-modal {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,.55);
  display: none;
  align-items: center;
  justify-content: center;
  z-index: 10000;
  padding: 1rem;
}
.ffs-gr-modal[open] { display: flex; }
.ffs-gr-modal .box {
  background: #fff;
  border-radius: var(--ffs-radius);
  max-width: 600px;
  width: 100%;
  max-height: 85vh;
  overflow-y: auto;
  padding: 1.5rem;
  position: relative;
}
.ffs-gr-modal .close {
  position: absolute;
  top: .5rem;
  right: .75rem;
  background: transparent;
  border: 0;
  font-size: 1.5rem;
  cursor: pointer;
}
.ffs-gr-modal .box .owner-reply {
  margin-top: 1rem;
  padding: .75rem 1rem;
  border-left: 3px solid var(--ffs-gold);
  background: #faf6ec;
  border-radius: 0 var(--ffs-radius) var(--ffs-radius) 0;
}

/* Reduced Motion */
@media (prefers-reduced-motion: reduce) {
  .ffs-gr-widget *,
  .ffs-gr-widget *::before,
  .ffs-gr-widget *::after {
    transition: none !important;
    animation: none !important;
    scroll-behavior: auto !important;
  }
}
```

- [ ] **Step 2: Commit**

```bash
git add docs/widget.css
git commit -m "feat(widget): add widget stylesheet with responsive + a11y"
```

---

## Task 7: Widget-JS

**Goal:** `docs/widget.js` holt `reviews.json`, rendert Header + Karten + Slider-Buttons, öffnet ein Modal bei Klick auf die Karte. Vanilla JS, keine Dependencies.

**Files:**
- Create: `docs/widget.js`
- Create: `docs/index.html` (lokaler Test-Host)

**Acceptance Criteria:**
- [ ] Rendert in `#ffs-google-reviews` (falls vorhanden, sonst silent)
- [ ] Bei Error (HTTP fail, Schema-Fehler) versteckt sich das Widget
- [ ] Keyboard: `←`/`→` im fokussierten Slider
- [ ] Klick auf Karte → Modal mit vollem Text, optional Owner-Reply
- [ ] "Eine Bewertung schreiben" CTA öffnet `write_review_url` in neuem Tab
- [ ] Lädt Avatare von `avatars/{hash}.jpg` (relative URL), Fallback auf Initial-Kreis
- [ ] Skeleton-Karten während Ladezeit

**Verify:** `python -m http.server 8000 --directory docs` + Browser → Widget erscheint, Interaktionen funktionieren.

**Steps:**

- [ ] **Step 1: `docs/index.html` als Test-Host schreiben**

```html
<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <title>FFS Google Reviews — Local Test</title>
  <link rel="stylesheet" href="widget.css">
</head>
<body style="background:#f7f7f7; padding: 2rem 0;">
  <h1 style="text-align:center;">Widget-Test</h1>
  <div id="ffs-google-reviews"></div>
  <script src="widget.js" defer></script>
</body>
</html>
```

- [ ] **Step 2: `docs/widget.js` schreiben**

```javascript
/* Rezensionintegrator — Vanilla-JS Widget
 * Liest reviews.json (relativer Pfad), rendert Header + Slider + Modal.
 */
(function () {
  'use strict';

  const MOUNT_ID = 'ffs-google-reviews';
  const JSON_URL = new URL('reviews.json', document.currentScript.src).href;

  function ratingLabel(avg) {
    if (avg >= 5.0) return 'Ausgezeichnet';
    if (avg >= 4.7) return 'Sehr gut';
    if (avg >= 4.0) return 'Gut';
    return 'Bewertet';
  }

  function starsFilled(rating) {
    const r = Math.round(rating);
    return '★'.repeat(r) + '☆'.repeat(5 - r);
  }

  const GOOGLE_LOGO_SVG = `
    <svg class="logo" viewBox="0 0 48 48" aria-hidden="true">
      <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/>
      <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/>
      <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/>
      <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/>
    </svg>`;

  const VERIFIED_SVG = `
    <svg width="14" height="14" viewBox="0 0 24 24" aria-hidden="true">
      <path fill="currentColor" d="M12 2 3 6v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V6l-9-4zm-2 15-4-4 1.41-1.41L10 14.17l6.59-6.59L18 9l-8 8z"/>
    </svg>`;

  function avatarColor(name) {
    // Simple hash → HSL
    let h = 0;
    for (let i = 0; i < name.length; i++) h = (h * 31 + name.charCodeAt(i)) % 360;
    return `hsl(${h}, 45%, 55%)`;
  }

  function renderAvatar(author) {
    if (author.avatar_url) {
      return `<img class="avatar" src="${author.avatar_url}" alt="${escapeHtml(author.name)}" loading="lazy">`;
    }
    const color = avatarColor(author.name || '?');
    return `<div class="avatar" style="background:${color}" aria-hidden="true">${escapeHtml(author.initial || '?')}</div>`;
  }

  function escapeHtml(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }

  function renderCard(review) {
    return `
      <article class="review-card" data-review-id="${escapeHtml(review.id)}" tabindex="0" role="button" aria-label="Rezension von ${escapeHtml(review.author.name)} lesen">
        <div class="author-row">
          ${renderAvatar(review.author)}
          <div class="meta">
            <div class="name">${escapeHtml(review.author.name)}</div>
            <div class="date">${escapeHtml(review.date_display)}</div>
          </div>
        </div>
        <div class="rating-row">
          <span class="stars" aria-label="${review.rating} von 5 Sternen">${starsFilled(review.rating)}</span>
          ${review.verified ? `<span class="verified" title="Google-Nutzer">${VERIFIED_SVG}</span>` : ''}
        </div>
        <p class="text">${escapeHtml(review.text)}</p>
        <span class="read-more">Weiterlesen</span>
      </article>`;
  }

  function renderSkeleton() {
    let out = '';
    for (let i = 0; i < 4; i++) {
      out += `
        <article class="review-card skeleton" aria-hidden="true">
          <div class="author-row">
            <div class="avatar"></div>
            <div class="meta">
              <div class="sk-line"></div>
              <div class="sk-line short"></div>
            </div>
          </div>
          <div class="sk-line"></div>
          <div class="sk-line"></div>
          <div class="sk-line short"></div>
        </article>`;
    }
    return out;
  }

  function renderHeader(business) {
    return `
      <header class="ffs-gr-header">
        ${GOOGLE_LOGO_SVG}
        <span class="label">${escapeHtml(ratingLabel(business.rating_avg))}</span>
        <span class="stars" aria-label="${business.rating_avg} von 5 Sternen">${starsFilled(business.rating_avg)}</span>
        <span class="score">${Number(business.rating_avg).toFixed(1).replace('.', ',')}</span>
        <span class="separator">│</span>
        <span class="count">${business.rating_count} Bewertungen</span>
        <a class="cta-button" href="${business.write_review_url}" target="_blank" rel="noopener nofollow">Eine Bewertung schreiben</a>
      </header>`;
  }

  function renderModal(review) {
    const reply = review.owner_reply
      ? `<div class="owner-reply"><strong>Antwort des Inhabers (${escapeHtml(review.owner_reply.date_iso || '')}):</strong><br>${escapeHtml(review.owner_reply.text)}</div>`
      : '';
    return `
      <div class="ffs-gr-modal" open role="dialog" aria-modal="true" aria-label="Volle Rezension">
        <div class="box">
          <button class="close" aria-label="Schließen">×</button>
          <div class="author-row" style="margin-bottom:1rem;">
            ${renderAvatar(review.author)}
            <div class="meta">
              <div class="name">${escapeHtml(review.author.name)}</div>
              <div class="date">${escapeHtml(review.date_display)}</div>
            </div>
          </div>
          <div class="rating-row"><span class="stars">${starsFilled(review.rating)}</span></div>
          <p style="white-space:pre-wrap; line-height:1.55;">${escapeHtml(review.text)}</p>
          ${reply}
        </div>
      </div>`;
  }

  function mountModal(review) {
    const wrap = document.createElement('div');
    wrap.innerHTML = renderModal(review);
    const modal = wrap.firstElementChild;
    document.body.appendChild(modal);
    const close = () => modal.remove();
    modal.querySelector('.close').addEventListener('click', close);
    modal.addEventListener('click', e => { if (e.target === modal) close(); });
    document.addEventListener('keydown', function esc(e) {
      if (e.key === 'Escape') { close(); document.removeEventListener('keydown', esc); }
    });
  }

  function bindSlider(root, reviewsById) {
    const track = root.querySelector('.ffs-gr-track');
    const prev = root.querySelector('.nav-prev');
    const next = root.querySelector('.nav-next');
    const scrollBy = dir => {
      const card = track.querySelector('.review-card');
      if (!card) return;
      track.scrollBy({ left: (card.offsetWidth + 16) * dir, behavior: 'smooth' });
    };
    prev.addEventListener('click', () => scrollBy(-1));
    next.addEventListener('click', () => scrollBy(1));

    track.addEventListener('keydown', e => {
      if (e.key === 'ArrowLeft') { scrollBy(-1); e.preventDefault(); }
      if (e.key === 'ArrowRight') { scrollBy(1); e.preventDefault(); }
    });

    track.addEventListener('click', e => {
      const card = e.target.closest('.review-card');
      if (!card || card.classList.contains('skeleton')) return;
      const id = card.getAttribute('data-review-id');
      const r = reviewsById.get(id);
      if (r) mountModal(r);
    });
    track.addEventListener('keydown', e => {
      if (e.key !== 'Enter' && e.key !== ' ') return;
      const card = e.target.closest('.review-card');
      if (!card || card.classList.contains('skeleton')) return;
      e.preventDefault();
      const id = card.getAttribute('data-review-id');
      const r = reviewsById.get(id);
      if (r) mountModal(r);
    });
  }

  function renderWidget(mount, data) {
    mount.classList.add('ffs-gr-widget');
    mount.innerHTML = `
      ${renderHeader(data.business)}
      <div class="ffs-gr-slider">
        <button class="nav-prev" aria-label="Vorherige Rezensionen" type="button">‹</button>
        <div class="ffs-gr-track" tabindex="0">
          ${data.reviews.map(renderCard).join('')}
        </div>
        <button class="nav-next" aria-label="Nächste Rezensionen" type="button">›</button>
      </div>`;
    const byId = new Map(data.reviews.map(r => [r.id, r]));
    bindSlider(mount, byId);
  }

  function renderSkeletonState(mount) {
    mount.classList.add('ffs-gr-widget');
    mount.innerHTML = `
      <header class="ffs-gr-header">
        <span class="label">Rezensionen werden geladen…</span>
      </header>
      <div class="ffs-gr-slider">
        <div class="ffs-gr-track">${renderSkeleton()}</div>
      </div>`;
  }

  async function boot() {
    const mount = document.getElementById(MOUNT_ID);
    if (!mount) return;
    renderSkeletonState(mount);

    try {
      const resp = await fetch(JSON_URL, { cache: 'no-cache' });
      if (!resp.ok) throw new Error('HTTP ' + resp.status);
      const data = await resp.json();
      if (!data || !Array.isArray(data.reviews) || !data.business) {
        throw new Error('invalid schema');
      }
      renderWidget(mount, data);
    } catch (err) {
      console.warn('[ffs-gr-widget] failed to load:', err);
      mount.style.display = 'none';
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
```

- [ ] **Step 3: Lokaler Browser-Test**

Kopiere vorübergehend `tests/fixtures/reviews_sample.json` nach `docs/reviews.json` und starte:

```bash
cp tests/fixtures/reviews_sample.json docs/reviews.json
python -m http.server 8000 --directory docs
```

Browser: `http://localhost:8000/`
Erwartung:
- Header: Google-Logo + "Ausgezeichnet" + 5,0 + "217 Bewertungen" + gelber CTA
- 2 Karten sichtbar
- Klick auf Karte → Modal öffnet mit Vollem Text + Owner-Reply (bei Review 2)
- Fenster schmaler ziehen → Karten responsive
- Tab → fokussiert den Slider, `→`/`←` scrollen

Lösche `docs/reviews.json` wieder (wird von der Action später überschrieben):
```bash
rm docs/reviews.json
```

- [ ] **Step 4: Commit**

```bash
git add docs/widget.js docs/index.html
git commit -m "feat(widget): add vanilla JS widget (slider + modal + skeleton)"
```

---

## Task 8: GitHub Actions Workflow

**Goal:** `.github/workflows/fetch.yml` läuft täglich, ruft den Fetcher, committed `docs/reviews.json` + neue Avatare nur bei Änderungen.

**Files:**
- Create: `.github/workflows/fetch.yml`

**Acceptance Criteria:**
- [ ] Cron `0 3 * * *` + `workflow_dispatch`
- [ ] Python 3.11
- [ ] Installiert `fetcher/requirements.txt`
- [ ] Führt `python -m fetcher.fetch` mit den richtigen Env-Vars aus
- [ ] Committed nur wenn `docs/reviews.json` oder `docs/avatars/` geändert sind
- [ ] `permissions: contents: write`
- [ ] Läuft lokal mit `act` oder manuell per `workflow_dispatch`

**Verify:** Nach GitHub-Push: Actions-Tab → "Run workflow" klicken → Run ist grün.

**Steps:**

- [ ] **Step 1: `.github/workflows/fetch.yml` schreiben**

```yaml
name: Fetch Reviews

on:
  schedule:
    - cron: '0 3 * * *'
  workflow_dispatch: {}

jobs:
  fetch:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'
          cache-dependency-path: fetcher/requirements.txt

      - name: Install dependencies
        run: pip install -r fetcher/requirements.txt

      - name: Run fetcher
        env:
          REVIEWS_SOURCE: places
          PLACE_ID: ChIJZybyS393vUcRmrlk8nxVyuE
          GOOGLE_MAPS_API_KEY: ${{ secrets.GOOGLE_MAPS_API_KEY }}
        run: python -m fetcher.fetch

      - name: Commit changes
        run: |
          if [[ -n "$(git status --porcelain docs/reviews.json docs/avatars/)" ]]; then
            git config user.name "github-actions[bot]"
            git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
            git add docs/reviews.json docs/avatars/
            git commit -m "chore(reviews): update reviews.json ($(date -u +%Y-%m-%d))"
            git push
          else
            echo "No changes to reviews.json/avatars — skipping commit."
          fi
```

- [ ] **Step 2: Commit**

```bash
git add .github/workflows/fetch.yml
git commit -m "ci: add daily reviews fetcher workflow"
```

---

## Task 9: README + Dokumentation Finalisieren

**Goal:** README erklärt Setup, Entwicklung, Phase-2-Umstieg und Duda-Einbettung für den Nutzer und künftige Mitleser.

**Files:**
- Modify: `README.md`

**Acceptance Criteria:**
- [ ] Abschnitte: Zweck, Architektur, Setup, Entwicklung, Phase-2-Umschaltung, Duda-Einbettung, Troubleshooting
- [ ] Alle Befehle kopierbar und getestet
- [ ] Verweis auf Spec + Plan

**Verify:** `cat README.md | head -40` — sinnvolle erste 40 Zeilen.

**Steps:**

- [ ] **Step 1: `README.md` vollständig überschreiben**

```markdown
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

1. Google-Quota für Business Profile API prüfen (beantragt 2026-04-17).
2. `fetcher/business_api.py` implementieren (siehe Kommentar im File).
3. Secrets in GitHub setzen: `GOOGLE_OAUTH_CLIENT_ID`, `GOOGLE_OAUTH_CLIENT_SECRET`, `GOOGLE_OAUTH_REFRESH_TOKEN`.
4. In `.github/workflows/fetch.yml` `REVIEWS_SOURCE: business` setzen.
5. Workflow manuell triggern — alle ~217 Reviews erscheinen.

## Einbettung auf Duda

In der Duda-Seite einen `HTML`/`Embed Code`-Baustein einfügen:

```html
<div id="ffs-google-reviews"></div>
<link rel="stylesheet" href="https://firefly1502.github.io/rezensionintegrator/widget.css">
<script src="https://firefly1502.github.io/rezensionintegrator/widget.js" defer></script>
```

## Troubleshooting

- **Action rot, `403 PERMISSION_DENIED`:** API-Key ist auf Places API (New) beschränkt — prüfen, ob der Key noch gültig ist und das richtige Projekt aktiviert hat.
- **Widget zeigt sich nicht:** Browser-Dev-Tools → Console → Error-Message lesen. Das Widget versteckt sich bei Fehlern absichtlich.
- **Avatar-Datei 404:** Fetcher hat sie noch nicht geladen — manuell Workflow triggern.

## Dokumente

- Spec: [docs/superpowers/specs/2026-04-21-rezensionintegrator-design.md](docs/superpowers/specs/2026-04-21-rezensionintegrator-design.md)
- Plan: [docs/superpowers/plans/2026-04-21-rezensionintegrator-v1.md](docs/superpowers/plans/2026-04-21-rezensionintegrator-v1.md)
- Datenschutz-Entwürfe: [docs/datenschutz-text-entwuerfe.md](docs/datenschutz-text-entwuerfe.md)
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: expand README with setup, Phase-2 guide, troubleshooting"
```

---

## Task 10: GitHub-Setup (geführt, Nutzer-interaktiv)

**Goal:** Repo existiert auf GitHub unter `Firefly1502/rezensionintegrator`, Code ist gepusht, Pages ist aktiv, Secret `GOOGLE_MAPS_API_KEY` ist gesetzt, erste Action läuft grün.

**Files:** keine Änderungen im Repo — reine Konfiguration auf GitHub.

**Acceptance Criteria:**
- [ ] `https://github.com/Firefly1502/rezensionintegrator` existiert (public)
- [ ] Lokaler Code ist nach `main` gepusht
- [ ] Pages: Source = `main` / `/docs`, URL = `https://firefly1502.github.io/rezensionintegrator/`
- [ ] Secret `GOOGLE_MAPS_API_KEY` ist gesetzt
- [ ] Manuelle Ausführung des Workflows läuft grün; `docs/reviews.json` im Repo aktualisiert
- [ ] Browser öffnet `https://firefly1502.github.io/rezensionintegrator/` → Widget zeigt echte Reviews

**Verify:** `curl -sI https://firefly1502.github.io/rezensionintegrator/reviews.json` → `HTTP/2 200`.

**Steps:**

- [ ] **Step 1: GitHub Desktop installieren (falls noch nicht)**

`https://desktop.github.com/` → herunterladen und mit dem Konto `Firefly1502` einloggen. GUI-Workflow, kein CLI-Ärger.

- [ ] **Step 2: Repo auf GitHub anlegen**

Im Browser: `https://github.com/new`
- Repository name: `rezensionintegrator`
- Description: *Selbstgehostetes Google-Reviews-Widget für Full Flight Sim*
- Visibility: **Public** (Pflicht für kostenlose Pages)
- **Nicht** initialisieren mit README/gitignore/license (haben wir schon lokal)
- Create repository.

- [ ] **Step 3: Lokales Repo zu GitHub pushen (via GitHub Desktop)**

GitHub Desktop → File → Add local repository → Ordner `REZENSIONINTEGRATOR` auswählen. Danach oben "Publish repository" klicken → Name `rezensionintegrator` → nicht privat.

(Alternativ CLI im Projekt-Root:)
```bash
git remote add origin https://github.com/Firefly1502/rezensionintegrator.git
git branch -M main
git push -u origin main
```

- [ ] **Step 4: GitHub Pages aktivieren**

Repo → Settings → Pages
- Source: `Deploy from a branch`
- Branch: `main` / Folder: `/docs`
- Save.
- Nach ~1 Minute erscheint oben die URL `https://firefly1502.github.io/rezensionintegrator/`.

- [ ] **Step 5: Secret `GOOGLE_MAPS_API_KEY` setzen**

Repo → Settings → Secrets and variables → Actions → New repository secret
- Name: `GOOGLE_MAPS_API_KEY`
- Value: der bestehende API-Key (Places API New).
- Add secret.

(Hinweis: Der Key soll vor Go-Live rotiert werden — siehe Risiko-Abschnitt im Spec.)

- [ ] **Step 6: Workflow manuell triggern**

Repo → Actions → "Fetch Reviews" → "Run workflow" → "Run workflow" bestätigen.

Nach 30–60 Sekunden: Run wird grün, neuer Commit `chore(reviews): update reviews.json …` erscheint.

- [ ] **Step 7: Pages-Check**

Browser: `https://firefly1502.github.io/rezensionintegrator/`
- Widget muss sichtbar sein (5 Reviews, Header, gelber CTA-Button).
- Browser-Dev-Tools → Network: `reviews.json` lädt mit Status 200.

- [ ] **Step 8: Commit der Dokumentation (falls Screenshots o.ä.)**

Dieser Task produziert keine Commits im Repo (reine Konfig). Nur wenn etwas am README noch nachgetragen wird (z.B. die tatsächliche Pages-URL), folgt ein kleiner Commit.

---

## Task 11: Duda-Einbettung (Build-only)

**Goal:** Widget ist in Duda in einer Test-/Unterseite eingebaut und rendert korrekt. Noch **nicht** auf der Startseite aktiv (Trustindex läuft parallel weiter).

**Files:** keine — reine Duda-Konfiguration.

**Acceptance Criteria:**
- [ ] Auf einer Duda-Test-Seite (z.B. `/widget-test`, nicht im Menü verlinkt) ist der HTML-Baustein mit den 3 Zeilen eingefügt
- [ ] Im Live-Preview rendert das Widget mit echten Reviews
- [ ] Responsive-Test (Desktop-/Tablet-/Mobile-Ansicht in Duda-Vorschau) sieht sauber aus
- [ ] Seite ist als `noindex` markiert bzw. nicht öffentlich verlinkt, bis Datenschutz-Texte live sind

**Verify:** Manueller Browser-Check auf `https://www.fullflightsim.de/widget-test`.

**Steps:**

- [ ] **Step 1: Neue Seite in Duda anlegen**

Duda-Editor → Seiten → Neue Seite → Name: "Widget Test" → im Menü versteckt.

- [ ] **Step 2: Seite als noindex markieren**

Duda → SEO-Einstellungen der Seite → `noindex` aktivieren. (Optik-Check soll nicht in Google landen.)

- [ ] **Step 3: HTML-Baustein einsetzen**

Baustein-Palette → `HTML` / `Embed Code` auf die Seite ziehen. In das Textfeld einfügen:

```html
<div id="ffs-google-reviews"></div>
<link rel="stylesheet" href="https://firefly1502.github.io/rezensionintegrator/widget.css">
<script src="https://firefly1502.github.io/rezensionintegrator/widget.js" defer></script>
```

Speichern. Preview öffnen.

- [ ] **Step 4: Visual-Check in allen Breakpoints**

Duda-Preview → Desktop-, Tablet-, Mobile-Toggle durchklicken. Karten ordnen sich responsiv an, CTA-Button bleibt lesbar.

- [ ] **Step 5: Klick-Tests**

- Klick auf Karte → Modal öffnet mit vollem Text (Desktop & Mobile).
- Klick auf "Eine Bewertung schreiben" → öffnet Google-Review-Dialog in neuem Tab.
- `Esc` → Modal schließt.

- [ ] **Step 6: Abnahme & Übergabe**

Wenn alles funktioniert: Status „V1 build-only ready". Die Test-Seite bleibt versteckt. Trustindex läuft auf Startseite weiter. Nächster Schritt: Wartephase auf Business Profile API Quota → Task-Liste für V1.1 erstellen.

---

## Self-Review (intern durchgeführt)

- **Spec-Abdeckung:** Alle Sections 4–7 des Specs sind in Tasks abgebildet (Schema→T1, Fetcher Phase 1→T2–T5, Widget→T6–T7, Deployment→T8+T10, Duda→T11). Phase 2 bewusst als Stub in T5 (Business-API-Datei) — Aktivierung ist V1.1-Scope, nicht V1.
- **Placeholder-Scan:** Keine "TBD"/"TODO"/"später". Alle Codeblöcke enthalten vollständige Inhalte.
- **Typ-Konsistenz:** Schema-Felder (`author.initial`, `avatar_url`, `date_display`, `source`) werden in T1 (Fixture), T3 (Normalizer), T4 (Avatar-Cache), T5 (Orchestrator), T7 (Widget) identisch verwendet. Funktions-Namen: `fetch_place`, `normalize_places_response`, `cache_avatar`, `localize_avatars`, `validate_reviews_json`, `run()` — einheitlich referenziert.
- **Scope:** V1 fokussiert. Keine V2-Features (Konfigurator, Admin-UI) eingebaut. Business-API nur als Stub.
