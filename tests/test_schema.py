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


def test_review_rating_non_numeric_fails():
    data = _load("reviews_sample.json")
    data["reviews"][0]["rating"] = "five"
    with pytest.raises(ValueError, match="rating"):
        validate_reviews_json(data)
