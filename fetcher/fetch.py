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

import requests

from fetcher.avatar_cache import cache_avatar  # noqa: F401 – imported for test-patching
from fetcher.business_api import fetch_all_reviews as fetch_business
from fetcher.normalize import normalize_business_response, normalize_places_response
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
    source = os.environ.get("REVIEWS_SOURCE", "places").lower()

    docs_dir = docs_dir or Path(__file__).resolve().parent.parent / "docs"
    avatars_dir = docs_dir / "avatars"

    log.info("Fetching reviews (source=%s, place_id=%s)", source, place_id)

    try:
        if source == "places":
            api_key = _require_env("GOOGLE_MAPS_API_KEY")
            raw = fetch_place(place_id, api_key)
            data = normalize_places_response(raw, place_id)
        elif source == "business":
            token_json = _require_env("GOOGLE_TOKEN_JSON")
            raw_reviews, biz_info = fetch_business(place_id, token_json)
            data = normalize_business_response(raw_reviews, biz_info)
        else:
            raise ValueError(f"Unknown REVIEWS_SOURCE: {source!r}")
    except requests.RequestException as e:
        # Google-API-Ausfall nach allen Retries: reviews.json bleibt unverändert,
        # Job endet grün (kein Failure-Mail-Rauschen bei transienten 5xx-Störungen).
        log.warning(
            "Google API nicht erreichbar nach Retries — reviews.json bleibt unverändert. Details: %s",
            e,
        )
        return

    # Localize avatars using the module-level cache_avatar so tests can patch
    # fetcher.fetch.cache_avatar and intercept every call here.
    for review in data.get("reviews", []):
        author = review.get("author") or {}
        author["avatar_url"] = cache_avatar(author.get("avatar_url"), avatars_dir)

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
