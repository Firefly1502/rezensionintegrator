"""Google Business Profile API Client (Phase 2).

Liest alle Rezensionen paginiert via OAuth2. Credentials werden als JSON-String
aus der Env-Var GOOGLE_TOKEN_JSON geladen — kein Browser-Login nötig.

Endpoints:
    mybusinessaccountmanagement.googleapis.com/v1/accounts
    mybusinessbusinessinformation.googleapis.com/v1/{account}/locations
    mybusiness.googleapis.com/v4/{location}/reviews  (paginiert, max 50/Seite)
"""

from __future__ import annotations

import json
import logging
import time

import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

log = logging.getLogger(__name__)

_SCOPES = ["https://www.googleapis.com/auth/business.manage"]
_ACCOUNT_BASE = "https://mybusinessaccountmanagement.googleapis.com/v1"
_INFO_BASE = "https://mybusinessbusinessinformation.googleapis.com/v1"
_GMB_BASE = "https://mybusiness.googleapis.com/v4"

_RETRYABLE_STATUS = {429, 500, 502, 503, 504}
_RETRY_BACKOFF_SECONDS = (2, 4, 8)


def _get_with_retry(url: str, *, headers: dict, params: dict | None = None,
                    timeout: int = 15) -> requests.Response:
    """GET mit Retry auf 429/5xx. Exponential backoff 2s/4s/8s (3 Versuche gesamt)."""
    attempts = len(_RETRY_BACKOFF_SECONDS) + 1
    last_resp: requests.Response | None = None
    for attempt in range(1, attempts + 1):
        last_resp = requests.get(url, headers=headers, params=params, timeout=timeout)
        if last_resp.status_code not in _RETRYABLE_STATUS:
            last_resp.raise_for_status()
            return last_resp
        if attempt == attempts:
            break
        wait = _RETRY_BACKOFF_SECONDS[attempt - 1]
        log.warning(
            "HTTP %d from %s — retry in %ds (attempt %d/%d)",
            last_resp.status_code, url, wait, attempt, attempts,
        )
        time.sleep(wait)
    assert last_resp is not None
    last_resp.raise_for_status()
    return last_resp


def _load_credentials(token_json: str) -> Credentials:
    info = json.loads(token_json)
    creds = Credentials.from_authorized_user_info(info, _SCOPES)
    if not creds.valid and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return creds


def _auth_headers(creds: Credentials) -> dict:
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return {
        "Authorization": f"Bearer {creds.token}",
        "Accept-Language": "de-DE",
    }


def _discover_location(creds: Credentials) -> tuple[str, str, str]:
    """Returns (full_location_name, biz_name, google_maps_url)."""
    headers = _auth_headers(creds)

    resp = _get_with_retry(f"{_ACCOUNT_BASE}/accounts", headers=headers)
    accounts = resp.json().get("accounts", [])
    if not accounts:
        raise ValueError("Kein Google My Business Account gefunden.")
    account_name = accounts[0]["name"]
    log.info("Account: %s", account_name)

    resp = _get_with_retry(
        f"{_INFO_BASE}/{account_name}/locations",
        headers=headers,
        params={"readMask": "name,title,metadata"},
    )
    locations = resp.json().get("locations", [])
    if not locations:
        raise ValueError(f"Keine Locations für '{account_name}' gefunden.")

    loc = locations[0]
    full_location_name = f"{account_name}/{loc['name']}"
    biz_name = loc.get("title", full_location_name)
    google_maps_url = loc.get("metadata", {}).get("mapsUri", "")
    log.info("Location: %s (%s)", full_location_name, biz_name)

    return full_location_name, biz_name, google_maps_url


def fetch_all_reviews(place_id: str, token_json: str) -> tuple[list[dict], dict]:
    """Holt alle Rezensionen paginiert via Business Profile API.

    Returns:
        (raw_reviews, business_info) — raw_reviews ist die Liste roher API-Dicts,
        business_info enthält name, google_url, place_id für die Normalisierung.
    """
    creds = _load_credentials(token_json)
    location_name, biz_name, google_maps_url = _discover_location(creds)

    headers = _auth_headers(creds)
    all_reviews: list[dict] = []
    next_page_token: str | None = None

    while True:
        params: dict = {"pageSize": 50}
        if next_page_token:
            params["pageToken"] = next_page_token

        resp = _get_with_retry(
            f"{_GMB_BASE}/{location_name}/reviews",
            headers=headers,
            params=params,
        )
        data = resp.json()
        batch = data.get("reviews", [])
        all_reviews.extend(batch)
        log.info("Fetched %d reviews (total: %d)", len(batch), len(all_reviews))

        next_page_token = data.get("nextPageToken")
        if not next_page_token:
            break

    return all_reviews, {
        "name": biz_name,
        "google_url": google_maps_url,
        "place_id": place_id,
    }
