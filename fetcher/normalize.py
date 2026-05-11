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


_STAR_MAP = {"ONE": 1, "TWO": 2, "THREE": 3, "FOUR": 4, "FIVE": 5}


def normalize_business_response(raw_reviews: list[dict], business_info: dict) -> dict:
    """Normalisiert Business Profile API Reviews ins reviews.json Schema.

    raw_reviews: Liste roher Review-Dicts aus mybusiness.googleapis.com/v4
    business_info: {"place_id": ..., "name": ..., "google_url": ...}
    """
    place_id = business_info["place_id"]
    write_review_url = f"https://search.google.com/local/writereview?placeid={place_id}"
    google_url = business_info.get("google_url", "")

    reviews_out = []
    for r in raw_reviews:
        reviewer = r.get("reviewer", {})
        author_name = reviewer.get("displayName", "")
        date_iso, date_display = _format_date_de(r["createTime"])

        reply = r.get("reviewReply")
        owner_reply = None
        if reply:
            reply_date_iso, _ = _format_date_de(reply.get("updateTime", r["createTime"]))
            owner_reply = {
                "text": reply.get("comment", ""),
                "date_iso": reply_date_iso,
            }

        reviews_out.append({
            "id": r.get("reviewId", ""),
            "author": {
                "name": author_name,
                "initial": _initial(author_name),
                "avatar_url": reviewer.get("profilePhotoUrl") or None,
                "profile_url": None,
            },
            "rating": _STAR_MAP.get(r.get("starRating", ""), 0),
            "date_iso": date_iso,
            "date_display": date_display,
            "text": r.get("comment", ""),
            "language": None,
            "verified": True,
            "photos": [],
            "owner_reply": owner_reply,
            "source_url": google_url,
        })

    reviews_out.sort(key=lambda rev: rev["date_iso"], reverse=True)

    rating_values = [rev["rating"] for rev in reviews_out if rev["rating"] > 0]
    rating_avg = round(sum(rating_values) / len(rating_values), 1) if rating_values else 0.0

    return {
        "version": 1,
        "updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "source": "business_api",
        "business": {
            "place_id": place_id,
            "name": business_info["name"],
            "rating_avg": rating_avg,
            "rating_count": len(reviews_out),
            "google_url": google_url,
            "write_review_url": write_review_url,
        },
        "reviews": reviews_out,
    }
