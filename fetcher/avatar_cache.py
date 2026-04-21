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
