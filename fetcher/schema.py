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
