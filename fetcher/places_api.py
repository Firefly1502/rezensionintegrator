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
