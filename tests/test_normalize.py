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
