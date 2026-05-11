import json
from pathlib import Path

from fetcher.normalize import normalize_business_response, normalize_places_response
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


# ── Business API normalize ────────────────────────────────────────────────────

def _load_business():
    return json.loads((FIXTURES / "business_response_sample.json").read_text("utf-8"))


_BUSINESS_INFO = {
    "place_id": PLACE_ID,
    "name": "Full Flight Sim",
    "google_url": "https://maps.google.com/?cid=16252113413421686170",
}


def test_business_normalize_produces_valid_schema():
    result = normalize_business_response(_load_business(), _BUSINESS_INFO)
    validate_reviews_json(result)


def test_business_source_field():
    result = normalize_business_response(_load_business(), _BUSINESS_INFO)
    assert result["source"] == "business_api"


def test_business_reviews_sorted_newest_first():
    result = normalize_business_response(_load_business(), _BUSINESS_INFO)
    assert len(result["reviews"]) == 2
    assert result["reviews"][0]["date_iso"] == "2026-04-16"
    assert result["reviews"][1]["date_iso"] == "2026-04-10"


def test_business_review_fields_mapped():
    result = normalize_business_response(_load_business(), _BUSINESS_INFO)
    r = result["reviews"][0]
    assert r["author"]["name"] == "Max Mustermann"
    assert r["author"]["initial"] == "M"
    assert r["rating"] == 5
    assert r["text"] == "Absolut geiles Erlebnis!"
    assert r["owner_reply"] is None


def test_business_owner_reply_mapped():
    result = normalize_business_response(_load_business(), _BUSINESS_INFO)
    r = result["reviews"][1]
    assert r["owner_reply"]["text"] == "Danke für die tolle Bewertung!"
    assert r["owner_reply"]["date_iso"] == "2026-04-11"


def test_business_rating_avg_computed():
    result = normalize_business_response(_load_business(), _BUSINESS_INFO)
    assert result["business"]["rating_avg"] == 5.0
    assert result["business"]["rating_count"] == 2
    assert result["business"]["place_id"] == PLACE_ID
